"""
Created on April 2022

@author: Niko Suchowitz
"""
import readin_aux
import gap_finder
import glob
import time
from csv import *
import pandas as pd
import pathlib
import readin_to_year


def readin_data():
    """
    read in needed data and sort it completely to a whole year

    :return:
    """
    # start time to check how long program was running
    start_time = time.time()

    # define the year of the data
    year = '2021'

    # reset the csv-file which shows which countries have gaps
    with open("countries_w_gaps.csv", "w") as csvfile:
        # create a writer object with the needed attributes
        writer_obj = writer(csvfile, delimiter='\t')
        # write the header into the csv
        writer_obj.writerow(['Year', 'Country', 'Technology', 'AreaTypeCode', 'MissingPercentage'])

    # read in one csv-file
    #file_df = pd.read_csv('original_data/'+year+'/'+year+'_01_AggregatedGenerationPerType_16.1.B_C.csv', sep='\t', encoding='utf-8')

    # read in all the monthly csv-files of this country
    files = glob.glob('original_data/'+year+'/'+year+'_??_AggregatedGenerationPerType_16.1.B_C.csv', recursive=False)
    files.sort()
    for file in files:
        # get the string of the month from the file-names
        df_path = pathlib.PurePath(file).parts[2]
        month = df_path[5:7]

        # TODO: comment what is done here
        file_df = pd.read_csv(file, sep='\t', encoding='utf-8')
        file_df["DateTime"] = pd.to_datetime(file_df["DateTime"])
        file_df.sort_values(by='DateTime', inplace=True)
        file_df = file_df.reset_index(drop=True)
        # drop unnecesary coloms
        file_df = file_df.loc[:, ['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput']]

        # create list for all countries and save the list
        countries = readin_aux.list_countries(file_df)
        # if the list need to be checked for debug
        #with open("country_list.txt", "w") as file_object:
        #    file_object.write(str(countries))
        #    file_object.write("\n")
        #    file_object.write("Amount of Countries: " + str(len(countries)))

        # create list for all AreaTypeCodes and save the list
        atcodes = readin_aux.list_areatypecode(file_df)
        # if the list need to be checked for debug
        #with open("areatypecode_list.txt", "w") as file_object:
        #    file_object.write(str(atcodes))
        #    file_object.write("\n")
        #    file_object.write("Amount of AreaTypeCodes: " + str(len(atcodes)))

        # create list for all technologies and save the list
        technologies = readin_aux.list_technologies(file_df)
        # if the list need to be checked for debug
        #with open("technology_list.txt", "w") as file_object:
        #    file_object.write(str(technologies))
        #    file_object.write("\n")
        #    file_object.write("Amount of technologies: "+str(len(technologies)))

        # find all gaps for each technologie per country
        for atcode in atcodes:
            for technology in technologies:
                for country in countries:
                    gap_finder.check_for_gaps(file_df, atcode, country, technology, month, year)
        # TODO: need of double loop?
        # unify for every combination the year
        for atcode in atcodes:
            for technology in technologies:
                for country in countries:
                    # unify the year to fill the gaps afterwards
                    readin_to_year.unify_year(year, country, atcode, technology)


    # stop time to check how long program was running
    end_time = time.time()
    time_lapsed = end_time-start_time
    readin_aux.time_convert(time_lapsed)


if __name__ == '__main__':
    readin_data()
