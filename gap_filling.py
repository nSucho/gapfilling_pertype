"""
Created on April 2022

@author: Niko Suchowitz
"""
import pandas as pd
import filling_fedot
import filling_kalman
import gap_filling_aux
import numpy as np
import time
import readin_aux # only for the time calculation


def gapfill_main():
    """

    :return:
    :rtype:
    """
    # start time to check how long program was running
    start_time = time.time()

    # setting the values
    year = '2021'
    atc = 'CTY'
    country = 'DE'
    tech = 'Biomass'
    create_gaps = True

    # read in the file (and create gaps)
    original, data_w_nan = gap_filling_aux.read_in(year, atc, country, tech, create_gaps)
    original_series = np.array(original['ActualGenerationOutput'])

    # filling the gaps with the first fedot-methods and calculate the validation values
    #fedot_fwrd, fedot_bi = filling_fedot.fedot_frwd_bi(data_w_nan, country, year, atc, tech)
    # TODO: kick out again
    # for testing read in files instead of fill
    fedot_fwrd, fedot_bi = gap_filling_aux.readin_test(year, country, atc, tech, 'fedot', 'forward', 'bidirect')
    # create an array to calculate the validation
    fedot_fwrd_series = np.array(fedot_fwrd['ActualGenerationOutput'])
    fedot_bi_series = np.array(fedot_bi['ActualGenerationOutput'])
    # validate the gap_filling
    fedot_fwrd_dict = gap_filling_aux.validation(original_series, fedot_fwrd_series)
    fedot_bi_dict = gap_filling_aux.validation(original_series, fedot_bi_series)

    # filling the gaps with the second fedot-methods and calculate the validation values
    #fedot_ridge, fedot_comp = filling_fedot.fedot_ridge_composite(data_w_nan, country, year, atc, tech)
    # TODO: kick out again
    # for testing read in files instead of fill
    fedot_ridge, fedot_comp = gap_filling_aux.readin_test(year, country, atc, tech, 'fedot', 'ridge', 'composite')
    # create an array to calculate the validation
    fedot_ridge_series = np.array(fedot_ridge['ActualGenerationOutput'])
    fedot_comp_series = np.array(fedot_comp['ActualGenerationOutput'])
    # validate the gap_filling
    fedot_ridge_dict = gap_filling_aux.validation(original_series, fedot_ridge_series)
    fedot_comp_dict = gap_filling_aux.validation(original_series, fedot_comp_series)

    # filling the gaps with Kalman-filter and calculate the validation values
    #kalman_struct, kalman_arima = filling_kalman.kalman_method(data_w_nan, country, year, atc, tech)
    # TODO: kick out again
    # for testing read in files instead of fill
    kalman_struct, kalman_arima = gap_filling_aux.readin_test(year, country, atc, tech, 'kalman', 'structts', 'arima')
    # create an array to calculate the validation
    kalman_struct_series = np.array(kalman_struct['ActualGenerationOutput'])
    kalman_arima_series = np.array(kalman_arima['ActualGenerationOutput'])
    # validate the gap_filling
    kalman_struct_dict = gap_filling_aux.validation(original_series, kalman_struct_series)
    kalman_arima_dict = gap_filling_aux.validation(original_series, kalman_arima_series)

    # TODO: one more method

    print('FEDOT forward, bidirect: ', fedot_fwrd_dict, fedot_bi_dict)
    print('FEDOT ridge, composite: ', fedot_ridge_dict, fedot_comp_dict)
    print('Kalman structTS, arima: ', kalman_struct_dict, kalman_arima_dict)

    # plot
    #gap_filling_aux.plot_filling(original_series, fedot_fwrd_series, fedot_bi_series, kalman_struct_series,
    #                             kalman_arima_series)

    # stop time to check how long program was running
    end_time = time.time()
    time_lapsed = end_time - start_time
    readin_aux.time_convert(time_lapsed)


if __name__ == '__main__':
    gapfill_main()
