"""
Created on June 2021

@author: Niko Suchowitz
"""
import os
import pandas as pd
import numpy as np


def avg_week_method(data_w_nan, country, year, atc, tech, datatype, val_col, header):
    """
    fills the gaps using lineare interpolation and average of the week
    :param data_w_nan:
    :type data_w_nan:
    :param country:
    :type country:
    :param year:
    :type year:
    :param atc:
    :type atc:
    :param tech:
    :type tech:
    :return:
    :rtype:
    """
    # copy the df so we do not change the original
    df_w_nan_copy = data_w_nan.copy()

    # we add the week of the month to the rows
    df_w_nan_copy['Week'] = pd.factorize(df_w_nan_copy['DateTime'].dt.isocalendar().week)[0] + 1

    # ----------
    # now we fill all NaN's with the mean of this week
    # ----------
    avg_week = df_w_nan_copy[val_col].fillna(df_w_nan_copy.groupby('Week')[val_col].transform('mean'))

    # as second method we first fill up to 3h linear and everything longer with avg week
    # get the length of all gaps in the dataframe
    gap_length = df_w_nan_copy[val_col].isnull().astype(int).groupby(
        df_w_nan_copy[val_col].notnull().astype(int).cumsum()).sum()
    # get only the index of gaps which between one and three hours
    index_array = list(np.where(gap_length.between(1, 3)))
    # there is a shift over time of 'n' (amount of gaps until this point), so add it to the index
    n = 1
    # df_interpolated is an auxiliary dataframe with the linear-filled gaps
    df_interpolated = df_w_nan_copy[val_col].interpolate(method='linear')
    # iterate over all indices
    for index in index_array[0]:
        # l to not fill more than the gap-length
        l = 1
        length_of_gap = gap_length.loc[index+1]
        while l <= length_of_gap:
            # replace the gap with the value from the auxiliary dataframe
            df_w_nan_copy.loc[index+n, val_col] = df_interpolated.loc[index+n]
            l += 1
            n += 1
    # ----------
    # fill rest of the nan's with the "average-week"-method
    # ----------
    lin_avg_week = df_w_nan_copy[val_col].fillna(df_w_nan_copy.groupby('Week')[val_col].transform('mean'))

    # combine the values with the corresponding time
    df_avg_week = pd.concat([df_w_nan_copy['DateTime'], pd.Series(avg_week)], axis=1)
    df_lin_avg_week = pd.concat([df_w_nan_copy['DateTime'], pd.Series(lin_avg_week)], axis=1)

    # first check if folder exists to save data in
    isExist = os.path.exists('data/' + datatype + '/' + str(year) + '/' + country + '/avg_week')
    if not isExist:
        os.makedirs('data/' + datatype + '/' + str(year) + '/' + country + '/avg_week')

    # save the filled df as csv
    pd.DataFrame(df_avg_week).to_csv(
        'data/' + datatype + '/' + str(year) + '/' + country + '/avg_week/' + atc + '_' + tech + '_avg_week.csv',
        sep='\t', encoding='utf-8', index=False, header=header)
    pd.DataFrame(df_lin_avg_week).to_csv(
        'data/' + datatype + '/' + str(year) + '/' + country + '/avg_week/' + atc + '_' + tech + '_lin_avg_week.csv',
        sep='\t', encoding='utf-8', index=False, header=header)

    return df_avg_week, df_lin_avg_week
