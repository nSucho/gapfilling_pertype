"""
Created on April 2022

@author: Niko Suchowitz
"""
import pandas as pd
import glob
import csv


def unify_year(year, country, areatypecode, technology, datatype, val_col, header):
    """
    unifies the monthly data to a whole year
    :param year: year of the data
    :type year: string
    :param country: country code of the data
    :type country: string
    :param areatypecode: area type code of the data
    :type areatypecode: string
    :param technology: technology of the data
    :type technology: string
    :param datatype: data type of the data
    :type datatype: string
    :param val_col: header of the column with the important values
    :type val_col: string
    :param header: header which is used for the data
    :type header: list
    :return:
    :rtype:
    """
    # some (country, ATC, Technology)-combinations do not exist, so catch the error for them
    try:
        # read in all the monthly csv-files of this combination of country, atc and technology
        files = glob.glob(
            'data/' + datatype + '/' + str(year) + '/' + country + '/final_sorted/??_' + areatypecode + '_' +
            technology + '_?*', recursive=False)

        # concat to one dataframe and reset index
        df_year = pd.concat([pd.read_csv(file, sep='\t', encoding='utf-8') for file in files])
        df_year['DateTime'] = pd.to_datetime(df_year['DateTime'])
        df_year = df_year.reset_index(drop=True)
        df_year.sort_values(by='DateTime', inplace=True)

        # safe whole year as csv
        df_year.to_csv('data/' + datatype + '/' + str(year) + '/' + country + '/' + str(year) + '_' + areatypecode +
                       '_' + technology + '.csv', sep='\t', encoding='utf-8', index=False, header=header)

        # list the length of the gaps
        analyze_gap_length(df_year, year, country, areatypecode, technology, datatype, val_col)

    except Exception as e:
        #print("Error is found: "+str(e)+"||"+country+"--"+areatypecode+"--"+technology)
        pass


def analyze_gap_length(check_df, year, country, areatypecode, technology, datatype, val_col):
    """
    analyzes the length of the gaps in the dataframe
    :param check_df: dataframe to analyze
    :type check_df: dataframe
    :param year: year of the dataframe
    :type year: string
    :param country: country of the dataframe
    :type country: string
    :param areatypecode: area type code of the data
    :type areatypecode: string
    :param technology: technology of the data
    :type technology: string
    :param datatype: datatype of the data
    :type datatype: string
    :param val_col: header of the important column
    :type val_col: string
    :return:
    :rtype:
    """
    # works but only hands me the length
    """# TODO: funktioniert, verschiebt aber zeilen um summe der vorgänger nans, darum gibt erstmal nur länge zurück
    consecutive_gaps = check_df['ActualGenerationOutput'].isnull().astype(int).groupby(
            check_df['ActualGenerationOutput'].notnull().astype(int).cumsum()).sum()
    # drop zero values
    consecutive_gaps = consecutive_gaps.loc[consecutive_gaps != 0]
    consecutive_gaps.to_csv('data/'+str(year)+'/'+country+'/final_sorted_tech/'+str(month)+'_'+areatypecode+'_'
                                                    + technology+'_gaps_length.csv', sep='\t', encoding='utf-8', index=False,
                                                    header=['Length'])"""

    # works but count doesnt match the proper coloums
    """check_df['GapLength'] = check_df['ActualGenerationOutput'].isnull().astype(int).groupby(
            check_df['ActualGenerationOutput'].notnull().astype(int).cumsum()).sum()
    # drop zero values
    check_df.to_csv('data/'+str(year)+'/'+country+'/final_sorted_tech/'+str(month)+'_'+areatypecode+'_'
                                                    + technology+'_gaps_length.csv', sep='\t', encoding='utf-8', index=False,
                                                    header=['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput',
                                                                    'GapLength'])"""

    # gives back length of gaps as index and the amount of the gap-lengths per coloumn
    consecutive_gaps = check_df.apply(lambda d:consecutive_nans(d).value_counts()).fillna(0)
    # drop all coloums except val_col
    consecutive_gaps = consecutive_gaps[[val_col]]

    # get the gap-length as own column
    consecutive_gaps.reset_index(inplace=True)

    calc_missing_data(check_df, year, country, areatypecode, technology, val_col, datatype)

    consecutive_gaps.to_csv('data/' + datatype + '/' + str(year) + '/' + country + '/' + str(year) + '_' +
                            areatypecode + '_' + technology + '_gaps_length.csv', sep='\t', encoding='utf-8',
                            index=False, header=['GapLength', 'TotalAmountOfThisLength'])


def consecutive_nans(ds):
    """
    groups all gaps by their length and retruns how long they are
    :param ds: data with nans
    :type ds: dataframe
    :return: length of gaps as index and amount of gap-lengths per column
    :rtype:
    """
    return ds.isnull().astype(int).groupby(ds.notnull().astype(int).cumsum()).sum()


def calc_missing_data(df_to_check, year, country, areatypecode, technology, val_col, datatype):
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
    :return:
    :rtype:
    """
    # calc the percentage of missing data
    missing_data_o = df_to_check[val_col].isna().sum()
    missing_percent = (missing_data_o / len(df_to_check.index)) * 100

    # variable for saving the gaps-info later
    field_names = ['Year', 'Country', 'Technology', 'AreaTypeCode', 'MissingPercentage']
    gap_dict = {'Year': year, 'Country': country, 'Technology': technology, 'AreaTypeCode': areatypecode,
                'MissingPercentage': missing_percent}

    # save the country in the csv of countries with gaps
    with open("readin_SFTP/countries_w_gaps_sftp_"+datatype+"_"+year+".csv", "a") as csvfile:
        # create a dict_writer object with the needed attributes
        dictwriter_object = csv.DictWriter(csvfile, delimiter='\t', fieldnames=field_names)
        # write the dict into the csv
        dictwriter_object.writerow(gap_dict)
