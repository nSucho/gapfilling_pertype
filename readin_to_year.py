"""
Created on April 2022

@author: Niko Suchowitz
"""
import pandas as pd
import glob
import csv


def unify_year(year, country, areatypecode, technology, datatype, val_col, header):
    """

    :param year:
    :type year:
    :param country:
    :type country:
    :param areatypecode:
    :type areatypecode:
    :param technology:
    :type technology:
    :param datatype:
    :type datatype:
    :param val_col:
    :type val_col:
    :param header:
    :type header:
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

    :param check_df:
    :type check_df:
    :param year:
    :type year:
    :param country:
    :type country:
    :param areatypecode:
    :type areatypecode:
    :param technology:
    :type technology:
    :param datatype:
    :type datatype:
    :param val_col:
    :type val_col:
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

    calc_missing_data(check_df, year, country, areatypecode, technology, val_col)

    consecutive_gaps.to_csv('data/' + datatype + '/' + str(year) + '/' + country + '/' + str(year) + '_' +
                            areatypecode + '_' + technology + '_gaps_length.csv', sep='\t', encoding='utf-8',
                            index=False, header=['GapLength', 'TotalAmountOfThisLength'])


def consecutive_nans(ds):
    """

    :param ds:
    :type ds:
    :return:
    :rtype:
    """
    return ds.isnull().astype(int).groupby(ds.notnull().astype(int).cumsum()).sum()


def calc_missing_data(df_to_check, year, country, areatypecode, technology, val_col):
    """

    :param df_to_check:
    :type df_to_check:
    :param year:
    :type year:
    :param country:
    :type country:
    :param areatypecode:
    :type areatypecode:
    :param technology:
    :type technology:
    :param val_col:
    :type val_col:
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
    with open("countries_w_gaps.csv", "a") as csvfile:
        # create a dict_writer object with the needed attributes
        dictwriter_object = csv.DictWriter(csvfile, delimiter='\t', fieldnames=field_names)
        # write the dict into the csv
        dictwriter_object.writerow(gap_dict)
    # return missing_percent
