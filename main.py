"""
Created on April 2022

@author: Niko Suchowitz
"""
from auxiliary_methods import *
from gap_finder import checkForGaps
import glob
import time
from csv import *
import pandas as pd


def readin_data():
    """
    read in needed data

    :return:
    """
    # start time to check how long program was running
    start_time = time.time()

    year = '2021'
    # TODO: month properly
    month = 1

    # reset the csv-file with the countries with gaps
    with open("countries_w_gaps.csv", "w") as csvfile:
        # create a writer object with the needed attributes
        writer_obj = writer(csvfile, delimiter='\t')
        # write the header into the csv
        writer_obj.writerow(['Month', 'Country', 'Technology', 'AreaTypeCode', 'MissingPercentage'])

    # read in one csv-file
    #file_df = pd.read_csv('data/originals/2021_03_AggregatedGenerationPerType_16.1.B_C.csv', sep='\t', encoding='utf-8')

    # read in all the monthly csv-files of this country
    files = glob.glob('original_data/'+year+'/'+year+'_??_AggregatedGenerationPerType_16.1.B_C.csv', recursive=False)
    files.sort()

    for file in files:
        file_df = pd.read_csv(file, sep='\t', encoding='utf-8')
        file_df["DateTime"] = pd.to_datetime(file_df["DateTime"])
        file_df.sort_values(by='DateTime', inplace=True)
        file_df = file_df.reset_index(drop=True)
        # drop unnecesary coloms
        file_df = file_df.loc[:, ['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput']]

        # create list for all countries and save the list
        countries = list_countries(file_df)
        with open("country_list.txt", "w") as file_object:
            file_object.write(str(countries))
            file_object.write("\n")
            file_object.write("Amount of Countries: " + str(len(countries)))

        # create list for all AreaTypeCodes and save the list
        atcodes = list_areatypecode(file_df)
        with open("areatypecode_list.txt", "w") as file_object:
            file_object.write(str(atcodes))
            file_object.write("\n")
            file_object.write("Amount of AreaTypeCodes: " + str(len(atcodes)))

        # create list for all technologies and save the list
        technologies = list_technologies(file_df)
        with open("technology_list.txt", "w") as file_object:
            file_object.write(str(technologies))
            file_object.write("\n")
            file_object.write("Amount of technologies: "+str(len(technologies)))

        # find all gaps for each technologie per country
        for atcode in atcodes:
            for technology in technologies:
                for country in countries:
                    checkForGaps(file_df, atcode, country, technology, month, year)
        month += 1
    # TODO: unify_year irgendwo hier (ist in den aux_meths)
    #stop time to check how long program was running
    end_time = time.time()
    time_lapsed = end_time-start_time
    time_convert(time_lapsed)


if __name__ == '__main__':
    readin_data()
