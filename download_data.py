"""
Created on August 2022

@author: Niko Suchowitz
"""
from entsoe import EntsoePandasClient
import pandas as pd
import numpy as np
from readin_SFTP.readin_aux import create_path
from datetime import datetime as dt
from datetime import date
from readin_SFTP.readin_gap_finder import gap_list_creator
from csv import *


def download_files(token, data_type, year, timezone, country_code):
    """
    Method to download the files via ENTSO-E API and call all important methods to sort it afterwards
    :param token: the security token needed for connection
    :param data_type: the type of data to be downloaded; e.g. Actual Total Load
    :param year: year of the data
    :param timezone: in which timezone the DateTime-column should be
    :param country_code: country the data should be from
    :return:
    """
    # reset the countries_w_gaps.csv, to fill with new countries, which have gaps, later
    global df
    with open("countries_w_gaps_api_"+data_type+"_"+str(year)+".csv", "w") as csvfile:
        # create a writer object with the needed attributes
        writer_obj = writer(csvfile, delimiter='\t')
        # write the header into the csv
        writer_obj.writerow(['Year', 'Country', 'Technology', 'AreaTypeCode', 'MissingPercentage'])

    # to connect to entso-e a security token is needed
    client = EntsoePandasClient(api_key=token)
    # noinspection PyTypeChecker
    start = pd.Timestamp(str(year) + '0101', tz=timezone)  # pattern: yyyyMMddHHmm, tz = timezone
    # noinspection PyTypeChecker
    end = pd.Timestamp(str(year + 1) + '0101', tz=timezone)  # pattern: yyyyMMddHHmm, tz = timezone
    psr_type = None  # possible values can be found in the Guide under "A.5. PsrType"

    # checks which datatype should be downloaded
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
    # noinspection PyTypeChecker
    df.index = pd.to_datetime(df.index)
    # cut off the timezone
    df.index = df.index.tz_localize(None)
    # TODO: add correct atc
    # insert the area type code as a column
    atc = 'unknown'  # probably BZN
    df.insert(0, 'AreaTypeCode', atc)
    # insert the country code as a column
    df.insert(1, 'MapCode', country_code)

    if data_type == 'agpt':
        # create path
        path = 'data/' + data_type + '/api_data/' + str(year) + '/' + country_code + '/AfterDownload'
        create_path(path)
        # save the file with all techs
        df.to_csv(path + '/' + country_code + '_all.csv', sep='\t', encoding='utf-8', index=False)
        # sort the file and save all technologies in own file
        sort_agpt_files(agpt_df=df, path=path, country_code=country_code, atc=atc)
    else:
        # reshape to full hour
        df = reshape_api_data(df=df, val_col=val_col)
        # insert the technology as column for gap-filling
        tech = 'noTech'
        # save the file
        header = ['DateTime', 'AreaTypeCode', 'MapCode', 'TotalLoadValue']
        checkforgaps_api(df, atc, country_code, tech, year, val_col, header, data_type)


def sort_agpt_files(agpt_df, path, atc, country_code):
    """
    sorts the aggregated generation per type data into a proper form
    :param agpt_df: the dataframe to be sorted
    :param path: where it should be safed
    :param country_code: country of origin
    :return:
    """
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
            val_col = 'ActualGenerationOutput'
            header = ['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', val_col]
            checkforgaps_api(df_copy[header], atc, country_code, tech, year, val_col, header, data_type)


def reshape_api_data(df, val_col):
    """
    reshape the data into a full hour
    :param df: dataframe to reshape
    :param val_col: the name of the main column
    :return: reshaped dataframe
    """
    # resample to full hour
    df[val_col] = round((df.resample('H').mean()[val_col]), 2)
    # now drop the unnecessary rows
    df.dropna(subset=[val_col], inplace=True)
    # now set 'DateTime' back as column
    df.reset_index(inplace=True)
    return df


def checkforgaps_api(file_df_original, areatypecode, country, technology, year, val_col, header,
                     datatype):
    """

    :param file_df_original:
    :param areatypecode:
    :param country:
    :param technology:
    :param year:
    :param val_col:
    :param header:
    :param datatype:
    :return:
    """
    path = 'data/' + datatype + '/api_data/' + str(year) + '/' + country
    create_path(path + '/rawdata_sorted')
    create_path(path + '/final_sorted')
    create_path(path + '/gaplists')

    # ----------
    # check if start and end of month is in data
    # ----------
    # find out if first day is in list
    # first fill days, then hours
    firsttimestamp = (file_df_original['DateTime']).iloc[0]
    # check if 'firsttimestamp' is not first of the month
    if firsttimestamp.month != 1 or firsttimestamp.day != 1 or firsttimestamp.hour != 0:
        # if so create a datetime obj of the first day of month
        dayone = firsttimestamp.replace(month=1, day=1, hour=0)
        # now add to the sorted DF sorted_df, add in -1 pos and then add one to overall-index
        # if datatype == 'agpt' the column 'technology' is added
        if datatype == 'agpt':
            file_df_original.loc[-1] = (dayone, areatypecode, country, technology, np.nan)
        else:
            file_df_original.loc[-1] = (dayone, areatypecode, country, np.nan)
        file_df_original.index = file_df_original.index + 1
        file_df_original.sort_values(by='DateTime', inplace=True)
    # just to check if if-clause is working
    # else:
    # print("first of the month is in list")

    # now we check for the last of the month
    lastindex = len(file_df_original.index) - 1
    last_timestamp = file_df_original['DateTime'].iloc[lastindex]
    # first check if not current year, because if so it doesn't need to be filled up to the last day of the year
    if year != date.today().year:
        # checks if date is not last day of year or not last hour, then this date needs to be added
        if last_timestamp.date() != date(year, 12, 31) or last_timestamp.hour != int('23'):
            # if so we create a datetime with the last day and add it to the dataframe
            last_day_as_date = dt(year, 12, 31, 23)
            # if datatype == 'agpt' the column 'technology' is added
            if datatype == 'agpt':
                file_df_original.loc[-1] = (last_day_as_date, country, technology, areatypecode, np.nan)
            else:
                file_df_original.loc[-1] = (last_day_as_date, areatypecode, country, np.nan)
            file_df_original.index = file_df_original.index + 1
            file_df_original.sort_values(by='DateTime', inplace=True)
        # just to check if if-clause is working
        # else:
        # print("last of the month is in list")

    # save the auxiliary-dataframe into a csv
    file_df_original.to_csv(path + '/rawdata_sorted/' + areatypecode + '_' + technology + '.csv', sep='\t',
                            encoding='utf-8', index=False, header=header)
    # ----------
    # iterate to find the gaps
    # ----------
    # compare the date then time
    # init old datetime as first datetime of dataframe and create gap-list
    old_date = firsttimestamp
    gap_list = []
    # loop over every datetime-obj check if gap by comparing new and old
    for datetime in file_df_original['DateTime']:
        # set new_date to current datetime
        new_date = datetime
        # compare the time of the dates
        gap_list = gap_list_creator(old_date, new_date, gap_list, areatypecode, country, technology)
        # set the current datetime as old
        old_date = datetime

    # ----------
    # create a csv with all gaps included
    # ----------
    # convert list with the gaps to a dataframe
    gap_df = pd.DataFrame(gap_list)
    # check if the gap-df is empty
    if not gap_df.empty:
        # if the datatype is not '' we can drop the technology column
        if not datatype == 'agpt':
            gap_df = gap_df.drop(gap_df.columns[3], axis=1)
        gap_df.to_csv(path + '/gaplists/' + areatypecode + '_' + technology + '.csv', sep='\t', encoding='utf-8',
                      index=False, header=header)
        # concat both csv to have a list with filled in gaps then save as csv
        sorted_tech_csv = pd.read_csv(path + '/rawdata_sorted/' + areatypecode + '_' + technology + '.csv', sep='\t',
                                      encoding='utf-8')
        gap_list_csv = pd.read_csv(path + '/gaplists/' + areatypecode + '_' + technology + '.csv', sep='\t',
                                   encoding='utf-8')
        dataframes = [sorted_tech_csv, gap_list_csv]
        final_df = pd.concat(dataframes)
        # sort everything on the DateTime-column and save as csv
        final_df.sort_values(by='DateTime', inplace=True)
        final_df.reset_index(drop=True, inplace=True)
        # save the final df as csv
        final_df.to_csv(path + '/final_sorted/' + areatypecode + '_' + technology + '_wgaps.csv', sep='\t',
                        encoding='utf-8', index=False, header=header)
        # check how many entries missing
        calc_missing_data_api(final_df, year, country, areatypecode, technology, val_col, datatype, header)
    else:
        # print("there are no gaps")
        # sort everything on the DateTime-column and save as csv
        file_df_original.sort_values(by='DateTime', inplace=True)
        file_df_original.reset_index(drop=True, inplace=True)
        # save the final df as csv
        file_df_original.to_csv(path + '/final_sorted/' + areatypecode + '_' + technology + '_nogaps.csv', sep='\t',
                                encoding='utf-8', index=False, header=header)
        # check that no entries missing
        calc_missing_data_api(file_df_original, year, country, areatypecode, technology, val_col, datatype, header)


def calc_missing_data_api(df_to_check, year, country, areatypecode, technology, val_col, datatype, header):
    """
    check country for missing data and save that into a csv-file
    :param df_to_check: dataframe to check
    :type df_to_check: dataframe
    :param year: year of the dataframe
    :type year: string
    :param country: country code of the dataframe
    :type country: string
    :param areatypecode: area type code of the dataframe
    :type areatypecode: string
    :param technology: technology of the dataframe
    :type technology: string
    :param val_col: header of the column with the important values
    :type val_col: string
    :param header: list of all column names
    :type header: list
    :return:
    :rtype:
    """
    # calc the percentage of missing data
    df_to_check.columns = header
    missing_data_o = df_to_check[val_col].isna().sum()
    missing_percent = (missing_data_o / len(df_to_check.index)) * 100

    # variable for saving the gaps-info later
    field_names = ['Year', 'Country', 'Technology', 'AreaTypeCode', 'MissingPercentage']
    gap_dict = {'Year': year, 'Country': country, 'Technology': technology, 'AreaTypeCode': areatypecode,
                'MissingPercentage': missing_percent}

    # save the country in the csv of countries with gaps
    with open("countries_w_gaps_api_"+datatype+"_"+str(year)+".csv", "a") as csvfile:
        # create a dict_writer object with the needed attributes
        dictwriter_object = DictWriter(csvfile, delimiter='\t', fieldnames=field_names)
        # write the dict into the csv
        dictwriter_object.writerow(gap_dict)


if __name__ == '__main__':
    token = ''
    data_type = 'agpt'  # agpt or totalload
    year = 2022
    country_code = 'BA'
    timezone = 'CET'  # has to match with country (so GB -> WET) else inserting of the missing values goes wrong
    download_files(token, data_type, year, timezone, country_code)
