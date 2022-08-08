"""
Created on May 2022

@author: Niko Suchowitz
"""
import numpy as np
import pandas as pd
import os
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

imputeTS = importr('imputeTS')
kalman_StructTs = robjects.r['na_kalman']
kalman_auto_arima = robjects.r['na_kalman']


def kalman_method(data_w_nan, country, year, atc, tech, datatype, val_col, header):
    """
    fills the gaps with the kalman filter
    :param data_w_nan: dataframe containing the gaps
    :type data_w_nan: dataframe
    :param country: code of the country
    :type country: string
    :param year: year of the data
    :type year: string
    :param atc: area type code of the dataframe
    :type atc: string
    :param tech: technology of the dataframe
    :type tech: string
    :param datatype: type of the data
    :type datatype: string
    :param val_col: header of the column which contains the important values
    :type val_col: string
    :param header: whole header of the dataframe
    :type header: list
    :return: filled dataframes from kalman methods
    :rtype: dataframe
    """
    # copy the df so we do not change the original
    df_w_nan_copy = data_w_nan.copy()

    # values need to be a numeric vector
    w_gaps = np.ndarray.tolist(df_w_nan_copy[val_col].values)
    w_gaps = robjects.FloatVector(w_gaps)

    # ----------
    # StructTs-filling
    # ----------
    without_gaps_structts = np.array(kalman_StructTs(w_gaps, model="StructTS", smooth=True))

    # ----------
    # arima-filling
    # ----------
    # stepwise=False, approximation=False recommended in official documentation; code can be faster with deleting both
    # arguments, but then maybe less precise
    without_gaps_arima = np.array(kalman_StructTs(w_gaps, model="auto.arima", smooth=True, stepwise=False,
                                                  approximation=False))
    # first check if folder exists to save data in
    isExist = os.path.exists('data/' + datatype + '/' + str(year) + '/' + country + '/kalman')
    if not isExist:
        os.makedirs('data/' + datatype + '/' + str(year) + '/' + country + '/kalman')

    # combine filled values with date and time again
    df_structts = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gaps_structts)], axis=1)
    df_arima = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gaps_arima)], axis=1)
    # set header
    df_structts.columns = header
    df_arima.columns = header

    # save the combined df as csv
    pd.DataFrame(df_structts).to_csv('data/' + datatype + '/' + str(year) + '/' + country + '/kalman/' + atc + '_' +
                                     tech + '_filled_structts.csv', sep='\t', encoding='utf-8', index=False,
                                     header=header)
    pd.DataFrame(df_arima).to_csv('data/' + datatype + '/' + str(year) + '/' + country + '/kalman/' + atc + '_' + tech
                                  + '_filled_arima.csv', sep='\t', encoding='utf-8', index=False, header=header)

    return df_structts, df_arima
