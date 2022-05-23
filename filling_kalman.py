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


def kalman_method(data_w_nan, country, year, atc, tech):
    """
    The kalman-filter

    :param data_w_nan: the data with gaps (NaN) to fill
    :param country:
        :param year:
        :param atc:
        :param tech:
        :return: the data with filled gaps (NaN)
        """
    # copy the df so we do not change the original
    df_w_nan_copy = data_w_nan.copy()

    # TODO: 2x2 possibilities (smooth, not smooth, arima, structts)
    # values need to be a numeric vector
    w_gaps = np.ndarray.tolist(df_w_nan_copy['ActualGenerationOutput'].values)
    w_gaps = robjects.FloatVector(w_gaps)
    # StructTs-filling
    without_gaps_structts = np.array(kalman_StructTs(
        w_gaps, model="StructTS", smooth=True))
    # arima-filling
    without_gaps_arima = np.array(kalman_StructTs(
        w_gaps, model="auto.arima", smooth=True))

    # first check if folder exists to save data in
    isExist = os.path.exists('data/' + str(year) + '/' + country + '/kalman')
    if not isExist:
        os.makedirs('data/' + str(year) + '/' + country + '/kalman')

    # combine filled values with date and time again
    df_structts = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gaps_structts)], axis=1)
    df_arima = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gaps_arima)], axis=1)
    # set header
    df_structts.columns = ["DateTime", "ActualGenerationOutput"]
    df_arima.columns = ["DateTime", "ActualGenerationOutput"]

    # save the combined df as csv
    pd.DataFrame(df_structts).to_csv(
        'data/' + str(year) + '/' + country + '/kalman/' + atc + '_' + tech + '_filled_structts.csv',
        sep='\t', encoding='utf-8', index=False, header=['DateTime', 'ActualGenerationOutput'])
    pd.DataFrame(df_arima).to_csv(
        'data/' + str(year) + '/' + country + '/kalman/' + atc + '_' + tech + '_filled_arima.csv',
        sep='\t', encoding='utf-8', index=False, header=['DateTime', 'ActualGenerationOutput'])

    return df_structts, df_arima