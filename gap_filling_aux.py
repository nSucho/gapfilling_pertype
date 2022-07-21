"""
Created on April 2022

@author: Niko Suchowitz
"""
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd
import glob
# seed 10 is working with agpt and totalload
np.random.seed(10)


def read_in(datatype, year, atc, country, tech, create_gaps, duplicate_gaps, code_country_wgaps, atc_gaps, val_col,
            amount_gaps):
    """

    :param datatype:
    :type datatype:
    :param year:
    :type year:
    :param atc:
    :type atc:
    :param country:
    :type country:
    :param tech:
    :type tech:
    :param create_gaps:
    :type create_gaps:
    :param duplicate_gaps:
    :type duplicate_gaps:
    :param code_country_wgaps:
    :type code_country_wgaps:
    :param atc_gaps:
    :type atc_gaps:
    :param val_col:
    :type val_col:
    :param amount_gaps:
    :type amount_gaps:
    :return:
    :rtype:
    """
    # read in the file
    original = pd.read_csv('data/' + datatype + '/' + str(year) + '/' + country + '/' + str(year) + '_' + atc + '_' +
                           tech + '.csv', sep='\t', encoding='utf-8')
    # set 'DateTime' as datetime-type
    original['DateTime'] = pd.to_datetime(original['DateTime'])
    if create_gaps:
        data_w_nan = insert_gaps(original, val_col, amount_gaps)
    if duplicate_gaps:
        country_wgaps = pd.read_csv('data/' + datatype + '/' + str(year) + '/' + code_country_wgaps + '/' + str(year) +
                                    '_' + atc_gaps + '_' + tech + '.csv', sep='\t', encoding='utf-8')
        data_w_nan = duplicate_nans(original, country_wgaps, val_col)
    return original, data_w_nan


def insert_gaps(original, val_col, amount_gaps):
    """
    inserts gaps into the dataframe on a random basis
    :param original:
    :type original:
    :param val_col:
    :type val_col:
    :param amount_gaps:
    :type amount_gaps:
    :return:
    :rtype:
    """
    # create copy so we do not change original
    original_copy = original.copy()

    # randomly set frac-amount of the data to np.nan
    # frac = 0.1 means 10% of the data will be gaps
    for col in original_copy.columns:
        if col == val_col:
            original_copy.loc[original_copy.sample(frac=amount_gaps).index, col] = np.nan
    return original_copy


def duplicate_nans(df_wout_nan, gap_data, val_col):
    """
    duplicates the empty rows into a gapfree dataframe
    :param df_wout_nan: the dataframe we want to fill with gaps
    :type df_wout_nan:
    :param gap_data: mapcode of the dataframe we want to duplicate the gaps from
    :type gap_data:
    :param val_col:
    :type val_col:
    :return:
    :rtype:
    """
    # copy so we don't modify the original
    df_wout_copy = df_wout_nan.copy()

    # create an array of the indexes with nan
    nan_indexes = pd.isnull(gap_data).any(1).to_numpy().nonzero()

    # duplicate gaps in gap-less file
    for gap_index in nan_indexes[0]:
        df_wout_copy.loc[gap_index, val_col] = np.nan

    return df_wout_copy


def validation(original, filled_gaps):
    """

    :param original:
    :type original:
    :param filled_gaps:
    :type filled_gaps:
    :return:
    :rtype:
    """
    validation = [mean_absolute_error(original, filled_gaps), np.sqrt(mean_squared_error(original, filled_gaps)),
                  r2_score(original, filled_gaps)]
    return validation


def readin_test(datatype, year, country, atc, tech, name, method1, method2):
    # read in the file
    file_one = pd.read_csv('data/' + datatype + '/' + str(year) + '/' + country + '/' + name + '/' + atc + '_' + tech +
                           '_filled_' + method1 + '.csv', sep='\t', encoding='utf-8')
    file_two = pd.read_csv('data/' + datatype + '/' + str(year) + '/' + country + '/' + name + '/' + atc + '_' + tech +
                           '_filled_' + method2 + '.csv', sep='\t', encoding='utf-8')
    return file_one, file_two
