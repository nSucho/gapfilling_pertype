"""
Created on April 2022

couple of auxiliary functions for read_in.py

@author: Niko Suchowitz
"""
import os
import pandas as pd
import pathlib
import readin_gap_finder
import readin_to_year


def process_files(files, datatype, val_col, header, year):
    """

    :param files:
    :type files:
    :param datatype:
    :type datatype:
    :param val_col:
    :type val_col:
    :param header:
    :type header:
    :param year:
    :type year:
    :return:
    :rtype:
    """
    countries = set()
    atcodes = set()
    technologies = set()
    for file in files:
        # get all countries, areatypecodes and technologies
        file_df = pd.read_csv(file, sep='\t', encoding='utf-8')
        countries.update(list_countries(file_df))
        atcodes.update(list_areatypecode(file_df))
        if datatype == 'agpt':
            technologies.update(list_technologies(file_df))
    # convert all to a dataframe and save them as files
    pd.DataFrame(countries).to_csv('country_list.csv', sep='\t', encoding='utf-8', index=False, header=['Countries'])
    pd.DataFrame(atcodes).to_csv('areatypecode_list.csv', sep='\t', encoding='utf-8', index=False, header=['AreaTypeCodes'])
    if datatype == 'agpt':
        pd.DataFrame(technologies).to_csv('technology_list.csv', sep='\t', encoding='utf-8', index=False, header=['Technologies'])

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
                        readin_gap_finder.check_for_gaps(file_df, atcode, country, technology, month, year, val_col,
                                                         header, datatype)
        # ActTotLoad
        elif datatype == 'totalload':
            for atcode in atcodes:
                for country in countries:
                    readin_gap_finder.check_for_gaps(file_df, atcode, country, 'noTech', month, year, val_col, header,
                                                     datatype)
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

    :param file_df:
    :type file_df:
    :return:
    :rtype:
    """
    file_copy = file_df.copy()
    # take only the technologies of the country and drop the duplicates
    country_list = list(file_copy['MapCode'].drop_duplicates())
    country_list.sort()

    return country_list


def list_areatypecode(file_df):
    """

    :param file_df:
    :type file_df:
    :return:
    :rtype:
    """
    file_copy = file_df.copy()
    # take only the technologies of the country and drop the duplicates
    areatypecode_list = list(file_copy['AreaTypeCode'].drop_duplicates())
    areatypecode_list.sort()

    return areatypecode_list


def list_technologies(file_df):
    """

    :param file_df:
    :type file_df:
    :return:
    :rtype:
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

    :param path:
    :type path:
    :return:
    :rtype:
    """
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)


def time_convert(sec):
    """

    :param sec:
    :type sec:
    :return:
    :rtype:
    """
    mins = sec // 60
    secs = sec % 60
    hours = mins // 60
    mins = mins % 60

    print("Time needed for the program = {0}:{1}:{2}".format(int(hours), int(mins), int(secs)))

    with open("runtime.txt", "a") as file_object:
        file_object.write("Time needed for the program = {0}:{1}:{2}".format(int(hours), int(mins), int(secs)))
        file_object.write("\n")


def calc_missing_data(df_to_check):
    """

    :param df_to_check:
    :type df_to_check:
    :return:
    :rtype:
    """
    missing_data_o = df_to_check['ActualGenerationOutput'].isna().sum()
    missing_percent = (missing_data_o / len(df_to_check.index)) * 100

    return missing_percent
