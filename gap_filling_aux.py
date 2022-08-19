"""
Created on April 2022

@author: Niko Suchowitz
"""
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd
import glob
# seed 10 is working with agpt and totalload; only for gap_size 5 and 10
np.random.seed(10)


def read_in(origin_api, datatype, year, atc, country, tech, create_gaps, duplicate_gaps, copy_code, copy_atc, copy_tech,
            val_col, amount_gaps):
    """
    reads in the files needed for gap filling
    :param origin_api: checks if data from API or not
    :type origin_api: boolean
    :param datatype: type of the data
    :type datatype: string
    :param year: year of the gapless file
    :type year: string
    :param atc: area type code of the gapless file
    :type atc: string
    :param country: country code of the gapless file
    :type country: string
    :param tech: technology of the gapless file
    :type tech: string
    :param create_gaps: if true creates artifical gaps
    :type create_gaps: boolean
    :param duplicate_gaps: if true creates duplicated gaps
    :type duplicate_gaps: boolean
    :param copy_code: country code of the country with gaps
    :type copy_code: string
    :param copy_atc: area type code of the country with gaps
    :type copy_atc: string
    :param val_col: header of the column which contains the important values
    :type val_col: string
    :param amount_gaps: the amount of gaps inserted artificially into the country wihtout gaps
    :type amount_gaps: float
    :return:
    :rtype:
    """
    if origin_api:
        # read in the file
        original = pd.read_csv('data/' + datatype + '/api_data/' + str(year) + '/' + country + '/' + country + '_' +
                               tech + '.csv', sep='\t', encoding='utf-8')
    else:
        # read in the file
        original = pd.read_csv('data/' + datatype + '/' + str(year) + '/' + country + '/' + str(year) + '_' + atc + '_'
                               + tech + '.csv', sep='\t', encoding='utf-8')
    # set 'DateTime' as datetime-type
    original['DateTime'] = pd.to_datetime(original['DateTime'])
    # check if gaps should be created or duplicated, else just set the orignal as data_w_nan
    if create_gaps or duplicate_gaps:
        if create_gaps:
            data_w_nan = insert_gaps(original, val_col, amount_gaps)
        if duplicate_gaps:
            country_wgaps = pd.read_csv('data/' + datatype + '/' + str(year) + '/' + copy_code + '/' + str(year) +
                                        '_' + copy_atc + '_' + copy_tech + '.csv', sep='\t', encoding='utf-8')
            data_w_nan = duplicate_nans(original, country_wgaps, val_col)
    else:
        data_w_nan = original
    return original, data_w_nan


def insert_gaps(original, val_col, amount_gaps):
    """
    inserts gaps into the dataframe on a random basis
    :param original: original dataframe without gaps
    :type original: dataframe
    :param val_col: header of the column which contains the important values
    :type val_col: string
    :param amount_gaps: amount of gaps inserted into the original dataframe
    :type amount_gaps: float
    :return: dataframe with gaps
    :rtype: dataframe
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
    duplicates the empty rows of gap_data into a gapfree dataframe
    :param df_wout_nan: the dataframe we want to fill with gaps
    :type df_wout_nan: dataframe
    :param gap_data: dataframe we want to duplicate the gaps from
    :type gap_data: dataframe
    :param val_col: header of the column which contains the important values
    :type val_col: string
    :return: dataframe with gaps
    :rtype: dataframe
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
    validates the predicted data via MAE, RMSE and R^2
    :param original: original dataframe without gaps
    :type original: dataframe
    :param filled_gaps: dataframe with filled gaps
    :type filled_gaps: dataframe
    :return: validation values
    :rtype: list
    """
    validation = [mean_absolute_error(original, filled_gaps), np.sqrt(mean_squared_error(original, filled_gaps)),
                  r2_score(original, filled_gaps)]
    return validation
