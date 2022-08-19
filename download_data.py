"""
Created on August 2022

@author: Niko Suchowitz
"""
from entsoe import EntsoePandasClient
import pandas as pd
from readin_SFTP.readin_aux import create_path


# TODO: fit into readin_aux
# TODO: fit into gapfilling
def download_files(token, data_type, year, timezone, country_code):
    """"""
    # to connect to entso-e a security token is needed
    client = EntsoePandasClient(api_key=token)
    start = pd.Timestamp(str(year)+'0101', tz=timezone)  # pattern: yyyyMMddHHmm, tz = timezone
    end = pd.Timestamp(str(year+1)+'01010000', tz=timezone)  # pattern: yyyyMMddHHmm, tz = timezone
    psr_type = None  # possible values can be found in the Guide under "A.5. PsrType"

    if data_type == 'agpt':
        # download the data
        df = client.query_generation(country_code, start=start, end=end, psr_type=psr_type)
        if psr_type is None:
            # delete unnecessary multi-index
            try:
                df.columns = df.columns.droplevel(1)
            except Exception as e:
                print(e)
    if data_type == 'totalload':
        # download the data
        df = client.query_load(country_code, start=start, end=end)
        # give the column with the Values the proper name
        val_col = 'TotalLoadValue'
        df.rename(columns={'Actual Load': val_col}, inplace=True)

    # add name to index column and change to DateTime-Object
    df.index.name = 'DateTime'
    df.index = pd.to_datetime(df.index)
    # cut off the timezone
    df.index = df.index.tz_localize(None)
    # insert the country code as a column
    df.insert(0, 'MapCode', country_code)
    # TODO: add correct atc
    # insert the area type code as a column
    df.insert(1, 'AreaTypeCode', 'notSure')

    # create path
    path = 'data/' + data_type + '/api_data/' + str(year) + '/' + country_code
    create_path(path)
    if data_type == 'agpt':
        # save the file with all techs
        df.to_csv(path + '/' + country_code + '_all.csv', sep='\t', encoding='utf-8', index=False)
        # sort the file and save all technologies in own file
        sort_agpt_files(agpt_df=df, path=path, country_code=country_code)
    else:
        # reshape to full hour
        df = reshape_api_data(df=df, val_col=val_col)
        # insert the technology as column for gap-filling
        tech = 'noTech'
        df.insert(2, 'ProductionType', tech)
        # save the file
        df.to_csv(path + '/' + country_code + '_' + tech + '.csv', sep='\t', encoding='utf-8', index=False)


def sort_agpt_files(agpt_df, path, country_code):
    """"""
    # get the header of the dataframe as list
    column_names = agpt_df.columns.values.tolist()
    # loop over all header names
    for tech in column_names:
        # MapCode and AreaTypeCode is no technology so can be ignored
        if tech != 'MapCode' and tech != 'AreaTypeCode':
            # work only on the copy, so we don't have multiple 'ActualGenerationOutput'-columns in the end
            df_copy = agpt_df.copy()
            # rename the column for gap-filling later
            df_copy.rename(columns={tech: 'ActualGenerationOutput'}, inplace=True)
            # reshape to full hour
            df_copy = reshape_api_data(df=df_copy, val_col='ActualGenerationOutput')
            # insert the technology as column
            df_copy.insert(2, 'ProductionType', tech)
            # check if tech is
            if tech == 'Fossil Brown coal/Lignite':
                tech = 'Fossil Brown coal Lignite'
            # save only the necessary columns
            header = ['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput']
            df_copy.to_csv(path + '/' + country_code + '_' + tech + '.csv', sep='\t', encoding='utf-8', columns=header,
                           index=False)


def reshape_api_data(df, val_col):
    """"""
    # ----------
    # if the 'DateTime' is not in hourly steps, we down sample to hours
    # ----------
    # resample
    # TODO: does not round properly
    df[val_col] = round((df.resample('H').mean()[val_col]), 2)
    # now drop the unnecessary rows
    df.dropna(subset=[val_col], inplace=True)
    # now set 'DateTime' back as column
    df.reset_index(inplace=True)
    return df


if __name__ == '__main__':
    token = ''
    data_type = 'totalload'  # agpt or totalload
    year = 2021
    country_code = 'GB'
    timezone = 'EET'
    download_files(token, data_type, year, timezone, country_code)
