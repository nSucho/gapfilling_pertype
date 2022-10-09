"""
Created on April 2022

couple of auxiliary functions for read_in.py

@author: Niko Suchowitz
"""
import os
import pandas as pd
import numpy as np
import pathlib
from readin_SFTP import readin_gap_finder
from readin_SFTP import readin_to_year
import calendar
import glob
from datetime import date


def process_files(origin_api, files, datatype, val_col, header, year):
    """
    calls all necessary functions to sort the data properly
    :param origin_api:
    :type origin_api:
    :param files: path to the files needed
    :type files: list
    :param datatype: type of the data
    :type datatype: string
    :param val_col: header of the important column
    :type val_col: string
    :param header: whole header for the dataframes
    :type header: list
    :param year: year of the data
    :type year: string
    :return:
    :rtype:
    """
    countries = set()
    atcodes = set()
    technologies = set()
    for file in files:
        # get all countries, areatypecodes and technologies into a set
        file_df = pd.read_csv(file, sep='\t', encoding='utf-8')
        countries.update(list_countries(file_df))
        atcodes.update(list_areatypecode(file_df))
        if datatype == 'agpt':
            technologies.update(list_technologies(file_df))
    # convert all to a dataframe and save them as files
    pd.DataFrame(countries).to_csv('../country_list.csv', sep='\t', encoding='utf-8', index=False, header=['Countries'])
    pd.DataFrame(atcodes).to_csv('../areatypecode_list.csv', sep='\t', encoding='utf-8', index=False,
                                 header=['AreaTypeCodes'])
    if datatype == 'agpt':
        pd.DataFrame(technologies).to_csv('../technology_list.csv', sep='\t', encoding='utf-8', index=False,
                                          header=['Technologies'])

    for file in files:
        # get the string of the month from the file-names
        df_path = pathlib.PurePath(file).parts[4]
        month = df_path[5:7]

        # read in the file
        file_df = pd.read_csv(file, sep='\t', encoding='utf-8')
        # change the type of the 'DateTime' column to datetime, then sort the dataframe from first to last of the month
        file_df['DateTime'] = pd.to_datetime(file_df["DateTime"])
        file_df.sort_values(by='DateTime', inplace=True)
        file_df = file_df.reset_index(drop=True)
        # drop unnecessary columns
        file_df = file_df.loc[:, header]

        # ----------
        # find all gaps for each technology per country
        # ----------
        # ActGenPerType
        if datatype == 'agpt':
            for atcode in atcodes:
                for technology in technologies:
                    for country in countries:
                        readin_gap_finder.check_for_gaps(file_df, atcode, country, technology, month, year,
                                                         val_col, header, datatype)
        # ActTotLoad
        elif datatype == 'totalload':
            for atcode in atcodes:
                for country in countries:
                    readin_gap_finder.check_for_gaps(file_df, atcode, country, 'noTech', month, year,
                                                     val_col, header, datatype)

    # check if no monthly files are missing, else create (only for years which are completely over)
    current_year = date.today().year
    if year != str(current_year):
        if datatype == 'agpt':
            for atcode in atcodes:
                for technology in technologies:
                    if technology == 'Fossil Brown coal/Lignite':
                        technology = 'Fossil Brown coal Lignite'
                    for country in countries:
                        # check if there is a file in the folder which fits the atc and country
                        check_files = glob.glob(
                            'data/' + datatype + '/' + str(year) + '/' + country + '/final_sorted/??_' + atcode + '_' +
                            technology + '_?*', recursive=False)
                        if check_files:
                            # check if any of the months are missing
                            month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
                            for month in month_list:
                                check_file = glob.glob('data/' + datatype + '/' + str(year) + '/' + country +
                                                       '/final_sorted/' + month + '_' + atcode + '_' + technology + '_?*')
                                if not check_file:
                                    # if a month is missing, create it
                                    last_day_of_month = calendar.monthrange(int(year), int(month))[1]
                                    # create the range of the month
                                    rng = pd.date_range(start=year + '-' + month + '-01 00:00:00',
                                                        end=year + '-' + month + '-' + str(last_day_of_month) + ' 23:00:00',
                                                        freq='H', inclusive='both')
                                    # create the dataframe
                                    df = pd.DataFrame({'DateTime': rng, 'AreaTypeCode': atcode, 'MapCode': country,
                                                       'ProductionType': technology, 'ActualGenerationOutput': np.nan})
                                    # save the dataframe
                                    df.to_csv('data/' + datatype + '/' + str(year) + '/' + country + '/final_sorted/' +
                                              str(month) + '_' + atcode + '_' + technology + '_wgaps.csv', sep='\t',
                                              encoding='utf-8', index=False, header=header)
        # ActTotLoad
        elif datatype == 'totalload':
            for atcode in atcodes:
                for country in countries:
                    # check if there is a file in the folder which fits the atc and country
                    check_files = glob.glob(
                        'data/' + datatype + '/' + str(year) + '/' + country + '/final_sorted/??_' + atcode + '_' +
                        'noTech' + '_?*', recursive=False)
                    if check_files:
                        # check if any of the months are missing
                        month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
                        for month in month_list:
                            check_file = glob.glob('data/' + datatype + '/' + str(year) + '/' + country +
                                      '/final_sorted/' + month + '_' + atcode + '_' + 'noTech' + '_?*')
                            if not check_file:
                                # if a month is missing, create it
                                last_day_of_month = calendar.monthrange(int(year), int(month))[1]
                                # create the range of the month
                                rng = pd.date_range(start=year+'-'+month+'-01 00:00:00',
                                                    end=year+'-'+month+'-'+str(last_day_of_month)+' 23:00:00',
                                                    freq='H', inclusive='both')
                                # create the dataframe
                                df = pd.DataFrame({'DateTime': rng, 'AreaTypeCode': atcode, 'MapCode': country,
                                                   'TotalLoadvalue': np.nan})
                                # save the dataframe
                                df.to_csv('data/' + datatype + '/' + str(year) + '/' + country + '/final_sorted/' +
                                          str(month) + '_' + atcode + '_' + 'noTech' + '_wgaps.csv', sep='\t',
                                          encoding='utf-8', index=False, header=header)

    # unify for every combination the year to fill the gaps afterwards
    # ActGenPerType
    if datatype == 'agpt':
        for atcode in atcodes:
            for technology in technologies:
                if technology == 'Fossil Brown coal/Lignite':
                    technology = 'Fossil Brown coal Lignite'
                for country in countries:
                    readin_to_year.unify_year(year, country, atcode, technology, datatype, val_col, header)
    # ActTotLoad
    elif datatype == 'totalload':
        for atcode in atcodes:
            for country in countries:
                readin_to_year.unify_year(year, country, atcode, 'noTech', datatype, val_col, header)


def list_countries(file_df):
    """
    creates a list with all countries in the data
    :param file_df: dataframe to check
    :type file_df: dataframe
    :return: list of all countries
    :rtype: list
    """
    file_copy = file_df.copy()
    # take only the technologies of the country and drop the duplicates
    country_list = list(file_copy['MapCode'].drop_duplicates())
    country_list.sort()

    return country_list


def list_areatypecode(file_df):
    """
    creates a list with all area type codes in the data
    :param file_df: dataframe to check
    :type file_df: dataframe
    :return: list of all area type codes
    :rtype: list
    """
    file_copy = file_df.copy()
    # take only the technologies of the country and drop the duplicates
    areatypecode_list = list(file_copy['AreaTypeCode'].drop_duplicates())
    areatypecode_list.sort()

    return areatypecode_list


def list_technologies(file_df):
    """
    creates a list with all technologies in the data
    :param file_df: dataframe to check
    :type file_df: dataframe
    :return: list of all technologies
    :rtype: list
    """
    file_copy = file_df.copy()
    # take only the technologies of the country and drop the duplicates
    tech_list = file_copy['ProductionType'].drop_duplicates()

    # replace the '/' because else throws error
    tech_list = list(map(lambda x: x.replace('Fossil Brown coal/Lignite', r'Fossil Brown coal/Lignite'), tech_list))
    tech_list.sort()

    return tech_list


def create_path(path):
    """
    checks if a path already exists, if not creates it
    :param path: path to check
    :type path: string
    :return:
    :rtype:
    """
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)


def time_convert(sec):
    """
    stop watch
    :param sec: amount of time the code needed to run
    :type sec: int
    :return:
    :rtype:
    """
    mins = sec // 60
    secs = sec % 60
    hours = mins // 60
    mins = mins % 60

    print("Time needed for the program = {0}:{1}:{2}".format(int(hours), int(mins), int(secs)))

    with open("../runtime.txt", "a") as file_object:
        file_object.write("Time needed for the program = {0}:{1}:{2}".format(int(hours), int(mins), int(secs)))
        file_object.write("\n")


def calc_missing_data(df_to_check):
    """
    calculate the amount of missing data
    :param df_to_check: datframe whicht should be checked
    :type df_to_check: dataframe
    :return: amount of missing data
    :rtype: float
    """
    missing_data_o = df_to_check['ActualGenerationOutput'].isna().sum()
    missing_percent = (missing_data_o / len(df_to_check.index)) * 100

    return missing_percent
