"""
Created on April 2022

@author: Niko Suchowitz
"""

from readin_SFTP import readin_aux
import glob
import time
from csv import *


def readin_data(origin_api, datatype, year):
    """
    does some preperation for the sorting of the whole data and then starts the process
    :param origin_api:
    :param datatype:
    :param year:
    :return:
    """
    # start time to check how long program was running
    start_time = time.time()

    # reset the countries_w_gaps.csv, to fill with new countries, which have gaps, later
    with open("readin_SFTP/countries_w_gaps_sftp_"+datatype+"_"+year+".csv", "w") as csvfile:
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

    files.sort()
    readin_aux.process_files(origin_api, files, datatype, val_col, header, year)

    # stop time to check how long program was running
    end_time = time.time()
    time_lapsed = end_time - start_time
    readin_aux.time_convert(time_lapsed)


if __name__ == '__main__':
    # ----------
    # define the year and the type of the data
    # ----------
    year = '2021'
    # options for datatype => 'agpt' (ActGenPerType) or 'totalload'(ActTotLoad)
    datatype = 'totalload'
    origin_api = False

    readin_data(origin_api, datatype, year)
