"""
Created on April 2022

@author: Niko Suchowitz
"""
import pandas as pd
import filling_fedot
import filling_kalman
import filling_avg
import gap_filling_aux
import gap_filling_plotting
import numpy as np
import time
import readin_aux  # only for the time calculation
import os


def gapfill_main():
    """

    :return:
    :rtype:
    """
    # start time to check how long program was running
    start_time = time.time()

    # ----------
    # set the values
    # ----------
    # options for datatype => 'agpt' (ActGenPerType) or 'totalload'(ActTotLoad)
    datatype = 'agpt'
    # the year, AreaTypeCode, country and technology of the data which should be used for prediction
    year = '2021'
    atc = 'CTY'
    country = 'DE'
    tech = 'Biomass'
    # if 'create_gaps = True' there will be random gaps inserted into the data
    # if 'duplicate_gaps = True' the gaps from different file will be inserted into the data
    # one of both should be 'False'!
    create_gaps = True
    duplicate_gaps = False
    # country which the gaps should be duplicated from
    code_wgaps = 'BA'
    atc_gaps = 'BZN'
    # set the size of the sliding window for FEDOT and the amount of gaps which should be inserted in 'create_gaps'
    fedot_window = 250
    amount_gaps = 0.05  # 0.1 = 10% of the available data should be gaps
    # check the datatype and set the header accordingly
    if datatype == 'agpt':
        val_col = 'ActualGenerationOutput'
        header = ['DateTime', 'ActualGenerationOutput']
    elif datatype == 'totalload':
        # change tech to 'none' because the tables don't have a technology
        tech = 'none'
        val_col = 'TotalLoadValue'
        header = ['DateTime', 'TotalLoadValue']

    # ----------
    # read in the file (and create gaps)
    # ----------
    original, data_w_nan = gap_filling_aux.read_in(datatype, year, atc, country, tech, create_gaps, duplicate_gaps,
                                                   code_wgaps, atc_gaps, val_col, amount_gaps)
    original_series = np.array(original[val_col])

    # ----------
    # average of the week to fill the gaps and calculate the validation values
    # ----------
    avg_week, lin_avg_week = filling_avg.avg_week_method(data_w_nan, country, year, atc, tech, datatype, val_col,
                                                         header)
    # create an array to calculate the validation
    avg_week_series = np.array(avg_week[val_col])
    lin_avg_week_series = np.array(lin_avg_week[val_col])
    # validate the gap_filling
    avg_week_vali = gap_filling_aux.validation(original_series, avg_week_series)
    lin_avg_week_vali = gap_filling_aux.validation(original_series, lin_avg_week_series)

    # ----------
    # fedot-methods to fill the gaps and calculate the validation values
    # ----------
    fedot_fwrd, fedot_bi = filling_fedot.fedot_frwd_bi(data_w_nan, country, year, atc, tech, datatype, val_col, header,
                                                       fedot_window)
    # for testing read in files instead of fill
    # fedot_fwrd, fedot_bi = gap_filling_aux.readin_test(datatype, year, country, atc, tech, 'fedot', 'forward',
    #                                                   'bidirect')
    # create an array to calculate the validation
    fedot_fwrd_series = np.array(fedot_fwrd[val_col])
    fedot_bi_series = np.array(fedot_bi[val_col])
    # validate the gap_filling
    fedot_fwrd_vali = gap_filling_aux.validation(original_series, fedot_fwrd_series)
    fedot_bi_vali = gap_filling_aux.validation(original_series, fedot_bi_series)

    # ----------
    # Kalman-filter to fill gaps and calculate the validation values
    # ----------
    kalman_struct, kalman_arima = filling_kalman.kalman_method(data_w_nan, country, year, atc, tech, datatype, val_col,
                                                               header)
    # for testing read in files instead of fill
    # kalman_struct, kalman_arima = gap_filling_aux.readin_test(datatype, year, country, atc, tech, 'kalman', 'structts',
    #                                                          'arima')
    # create an array to calculate the validation
    kalman_struct_series = np.array(kalman_struct[val_col])
    kalman_arima_series = np.array(kalman_arima[val_col])
    # validate the gap_filling
    kalman_struct_vali = gap_filling_aux.validation(original_series, kalman_struct_series)
    kalman_arima_vali = gap_filling_aux.validation(original_series, kalman_arima_series)

    # ----------
    # plot
    # ----------
    # first check if folder exists to save data in
    isExist = os.path.exists('plots/' + datatype + '/' + year)
    if not isExist:
        os.makedirs('plots/' + datatype + '/' + year)
    # now plot
    gap_filling_plotting.plot_validation(avg_week_vali, lin_avg_week_vali, fedot_fwrd_vali, fedot_bi_vali,
                                         kalman_struct_vali, kalman_arima_vali, datatype, year, country, tech,
                                         fedot_window, amount_gaps)
    gap_filling_plotting.plot_filling(original, fedot_fwrd, fedot_bi, kalman_struct,
                                      kalman_arima, avg_week, lin_avg_week, val_col, datatype, year, country, tech,
                                      fedot_window, amount_gaps)

    # print the values for testing
    print('Average week, linear average week: ', avg_week_vali, lin_avg_week_vali)
    print('FEDOT forward, bidirect: ', fedot_fwrd_vali, fedot_bi_vali)
    print('Kalman structTS, arima: ', kalman_struct_vali, kalman_arima_vali)

    # stop time to check how long program was running
    end_time = time.time()
    time_lapsed = end_time - start_time
    readin_aux.time_convert(time_lapsed)


if __name__ == '__main__':
    gapfill_main()
