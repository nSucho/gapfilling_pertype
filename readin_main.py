"""
Created on April 2022

@author: Niko Suchowitz
"""
import numpy as np

import readin_aux
import glob
import time
from csv import *


def readin_data():
    """

    :return:
    :rtype:
    """
    # start time to check how long program was running
    start_time = time.time()

    # ----------
    # define the year and the type of the data
    # ----------
    year = '2018'
    # TODO: crossborder_flow missing
    # options for datatype => 'agpt' (ActGenPerType), 'totalload'(ActTotLoad), 'crossborder_flow'
    datatype = 'totalload'

    # reset the countries_w_gaps.csv, to fill with new countries, which have gaps, later
    with open("countries_w_gaps.csv", "w") as csvfile:
        # create a writer object with the needed attributes
        writer_obj = writer(csvfile, delimiter='\t')
        # write the header into the csv
        writer_obj.writerow(['Year', 'Country', 'Technology', 'AreaTypeCode', 'MissingPercentage'])

    # ----------
    # the read_in for 'Aggregated Generation per Type' (ENTSO-E Code: 16.1.B&C)
    # ----------
    if datatype == 'agpt':
        val_col = 'ActualGenerationOutput'
        header = ['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput']
        # get all the monthly csv-files
        files = glob.glob('data/agpt/original_data/' + year + '/'
                          + year + '_??_AggregatedGenerationPerType_16.1.B_C.csv', recursive=False)

    # ----------
    # the read_in for 'Actual Total Load' (ENTSO-E Code: 16.1.A)
    # ----------
    elif datatype == 'totalload':
        val_col = 'TotalLoadValue'
        header = ['DateTime', 'AreaTypeCode', 'MapCode', 'TotalLoadValue']
        # get all the monthly csv-files
        files = glob.glob('data/totalload/original_data/' + year + '/' + year + '_??_ActualTotalLoad_6.1.A.csv',
                          recursive=False)

    # ----------
    # the read_in for 'Physical Flows' (ENTSO-E Code: 12.1.G)
    # ----------
    # TODO: everything for crossborder; 12.1.G correct data?
    elif datatype == 'crossborder_flow':
        val_col = ''
        header = []
        # get all the monthly csv-files
        files = glob.glob('', recursive=False)
    files.sort()
    # TODO: neue function
    readin_aux.process_files(files, datatype, val_col, header, year)

    # stop time to check how long program was running
    end_time = time.time()
    time_lapsed = end_time - start_time
    readin_aux.time_convert(time_lapsed)


if __name__ == '__main__':
    readin_data()
