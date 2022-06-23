"""
Created on April 2022

couple of auxiliary functions for read_in.py

@author: Niko Suchowitz
"""
import os
import pandas as pd
import pathlib
import gap_finder
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

        # create list for all countries and save the list
        countries = list_countries(file_df)
        # create list for all AreaTypeCodes and save the list
        atcodes = list_areatypecode(file_df)

        # find all gaps for each technology per country
        if datatype == 'agpt':
            # create list for all technologies and save the list
            technologies = list_technologies(file_df)
            for atcode in atcodes:
                for technology in technologies:
                    for country in countries:
                        gap_finder.check_for_gaps(file_df, atcode, country, technology, month, year, val_col, header,
                                                  datatype)
            # TODO: need of double loop?
            # unify for every combination the year to fill the gaps afterwards
            for atcode in atcodes:
                for technology in technologies:
                    for country in countries:
                        readin_to_year.unify_year(year, country, atcode, technology, datatype, val_col, header)

        # find all gaps for each country
        elif datatype == 'totalload':
            # find all gaps for each technology per country
            for atcode in atcodes:
                for country in countries:
                    gap_finder.check_for_gaps(file_df, atcode, country, 'none', month, year, val_col, header, datatype)
            # TODO: need of double loop?
            # unify for every combination the year to fill the gaps afterwards
            for atcode in atcodes:
                for country in countries:
                    readin_to_year.unify_year(year, country, atcode, 'none', datatype, val_col, header)

        # TODO: erstellen
        elif datatype == 'crossborder_flow':
            pass


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

    # create df from list to save as csv
    country_df = pd.DataFrame(country_list)
    country_df.to_csv('country_list.csv', sep='\t', encoding='utf-8', index=False, header=['Countries'])

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

    # create df from list to save as csv
    atc_df = pd.DataFrame(areatypecode_list)
    atc_df.to_csv('areatypecode_list.csv', sep='\t', encoding='utf-8', index=False, header=['AreaTypeCodes'])

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
    tech_list = list(map(lambda x: x.replace('Fossil Brown coal/Lignite', 'Fossil Brown coal Lignite'), tech_list))
    tech_list.sort()

    # create df from list to save as csv
    tech_df = pd.DataFrame(tech_list)
    tech_df.to_csv('technology_list.csv', sep='\t', encoding='utf-8', index=False, header=['Technologies'])

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


# print("Created the new directory " +path)


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
