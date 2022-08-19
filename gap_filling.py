"""
Created on April 2022

@author: Niko Suchowitz
"""
import pandas as pd
import filling_fedot
import filling_kalman
import filling_avg
import gap_filling_aux
import numpy as np
import time
from readin_SFTP import readin_aux


# TODO: add optional variables
def gapfill_main(origin_api, datatype, year, country, atc, tech, copy_code, copy_atc, copy_tech, fedot_window, amount_gaps,
                 create_gaps, duplicate_gaps):
    """
    calls all necessary files to fill the gaps
    :param origin_api:
    :param datatype:
    :param year:
    :param country:
    :param atc:
    :param tech:
    :param copy_code:
    :param copy_atc:
    :param copy_tech:
    :param fedot_window:
    :param amount_gaps:
    :param create_gaps:
    :param duplicate_gaps:
    :return:
    """
    # start time to check how long program was running
    start_time = time.time()

    # check the datatype and set the header accordingly
    if datatype == 'agpt':
        val_col = 'ActualGenerationOutput'
        header = ['DateTime', 'ActualGenerationOutput']
    elif datatype == 'totalload':
        copy_tech = 'noTech'
        val_col = 'TotalLoadValue'
        header = ['DateTime', 'TotalLoadValue']

    # ----------
    # read in the file (and create gaps)
    # ----------
    # TODO: add origin
    original, data_w_nan = gap_filling_aux.read_in(origin_api, datatype, year, atc, country, tech, create_gaps,
                                                   duplicate_gaps, copy_code, copy_atc, copy_tech, val_col, amount_gaps)
    original_series = np.array(original[val_col])
    # ----------
    # average of the week to fill the gaps and calculate the validation values
    # ----------
    avg_week, lin_avg_week = filling_avg.avg_week_method(origin_api, data_w_nan, country, year, atc, tech, datatype,
                                                         val_col, header)
    # create an array to calculate the validation
    avg_week_series = np.array(avg_week[val_col])
    lin_avg_week_series = np.array(lin_avg_week[val_col])

    # ----------
    # fedot-methods to fill the gaps and calculate the validation values
    # ----------
    fedot_fwrd, fedot_bi = filling_fedot.fedot_frwd_bi(origin_api, data_w_nan, country, year, atc, tech, datatype,
                                                       val_col, header, fedot_window)
    # create an array to calculate the validation
    fedot_fwrd_series = np.array(fedot_fwrd[val_col])
    fedot_bi_series = np.array(fedot_bi[val_col])

    # ----------
    # Kalman-filter to fill gaps and calculate the validation values
    # ----------
    kalman_struct, kalman_arima = filling_kalman.kalman_method(origin_api, data_w_nan, country, year, atc, tech,
                                                               datatype, val_col, header)
    # create an array to calculate the validation
    kalman_struct_series = np.array(kalman_struct[val_col])
    kalman_arima_series = np.array(kalman_arima[val_col])

    # ----------
    # validation of the gap_filling
    # ----------
    if create_gaps or duplicate_gaps:
        # validate average week
        avg_week_vali = gap_filling_aux.validation(original_series, avg_week_series)
        lin_avg_week_vali = gap_filling_aux.validation(original_series, lin_avg_week_series)
        # validate fedot
        fedot_fwrd_vali = gap_filling_aux.validation(original_series, fedot_fwrd_series)
        fedot_bi_vali = gap_filling_aux.validation(original_series, fedot_bi_series)
        # validate the kalman
        kalman_struct_vali = gap_filling_aux.validation(original_series, kalman_struct_series)
        kalman_arima_vali = gap_filling_aux.validation(original_series, kalman_arima_series)

        # save the values for evaluation
        with open('plots/' + datatype + '/' + year + '/' + country + '_' + tech + '_' + str(amount_gaps) + '_' +
                  str(fedot_window) + '_' + 'results.txt', 'w') as file_object:
            file_object.write('Average week, linear average week: (MAE, SMAE, R\u00b2) ')
            file_object.write("\n")
            for listitem in avg_week_vali:
                file_object.write(str(round(listitem, 4)) + ', ')
            file_object.write("\n")
            for listitem in lin_avg_week_vali:
                file_object.write(str(round(listitem, 4)) + ', ')
            file_object.write("\n")
            file_object.write("\n")
            file_object.write('FEDOT forward, bidirect: (MAE, SMAE, R\u00b2) ')
            file_object.write("\n")
            for listitem in fedot_fwrd_vali:
                file_object.write(str(round(listitem, 4)) + ', ')
            file_object.write("\n")
            for listitem in fedot_bi_vali:
                file_object.write(str(round(listitem, 4)) + ', ')
            file_object.write("\n")
            file_object.write("\n")
            file_object.write('Kalman structTS, arima: (MAE, SMAE, R\u00b2) ')
            file_object.write("\n")
            for listitem in kalman_struct_vali:
                file_object.write(str(round(listitem, 4)) + ', ')
            file_object.write("\n")
            for listitem in kalman_arima_vali:
                file_object.write(str(round(listitem, 4)) + ', ')
            file_object.write("\n")
            file_object.write("\n")

    # ----------
    # plot
    # ----------
    # first check if folder exists to save data in
    """
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
    """

    # stop time to check how long program was running
    end_time = time.time()
    time_lapsed = end_time - start_time
    readin_aux.time_convert(time_lapsed)


if __name__ == '__main__':
    # options for datatype => 'agpt' (ActGenPerType) or 'totalload'(ActTotLoad)
    datatype = 'totalload'
    origin_api = False

    # the year, AreaTypeCode, country and technology of the data which should be used for prediction
    year = '2021'
    country = 'CY'
    atc = 'CTY'
    technologies = pd.read_csv('technology_list.csv', sep='\t', encoding='utf-8')

    # country which the gaps should be duplicated from
    copy_code = 'NIE'
    copy_atc = 'CTA'
    copy_tech = 'Wind Onshore'

    # set the size of the sliding window for FEDOT and the amount of gaps which should be inserted in 'create_gaps'
    fedot_window = 100
    amount_gaps = 0.2041  # 0.1 = 10% of the available data should be gaps

    # if 'create_gaps = True' there will be random gaps inserted into the data
    # if 'duplicate_gaps = True' the gaps from different file will be inserted into the data
    # one of both should be 'False'!
    create_gaps = False
    duplicate_gaps = False

    if datatype == 'agpt':
        # check all technologies for the country and atc combination
        for tech in technologies['Technologies'].to_list():
            try:
                gapfill_main(origin_api, datatype, year, country, atc, tech, copy_code, copy_atc, copy_tech,
                             fedot_window, amount_gaps, create_gaps, duplicate_gaps)
                print(tech + " excepted")
            except Exception as e:
                print(e)
    elif datatype == 'totalload':
        # change tech to 'none' because the tables don't have a technology
        tech = 'noTech'
        gapfill_main(origin_api, datatype, year, country, atc, tech, copy_code, copy_atc, copy_tech, fedot_window,
                     amount_gaps, create_gaps, duplicate_gaps)
