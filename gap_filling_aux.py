"""
Created on April 2022

@author: Niko Suchowitz
"""
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd
# seed 10 is working
np.random.seed(123)


def read_in(year, atc, country, tech, create_gaps):
    """

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
    :return:
    :rtype:
    """
    # read in the file
    original = pd.read_csv('data/' + str(year) + '/' + country + '/' + str(year) + '_' + atc + '_' +
                           tech + '.csv', sep='\t', encoding='utf-8')
    # set 'DateTime' as datetime-type
    original['DateTime'] = pd.to_datetime(original['DateTime'])
    if create_gaps:
        data_w_nan = insert_gaps(original)
    return original, data_w_nan


def insert_gaps(original):
    """
    inserts gaps into the dataframe on a random basis
    :param original:
    :type original:
    :return:
    :rtype:
    """
    # create copy so we do not change original
    original_copy = original.copy()

    # randomly set frac-amount of the data to np.nan
    # frac = 0.1 means 10% of the data will be gaps
    for col in original_copy.columns:
        if col == 'ActualGenerationOutput':
            original_copy.loc[original_copy.sample(frac=0.1).index, col] = np.nan
    return original_copy


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


# TODO: kick out later?
def readin_test(year, country, atc, tech, name, method1, method2):
    # read in the file
    file_one = pd.read_csv(
        'data/' + str(year) + '/' + country + '/' + name + '/' + atc + '_' + tech + '_filled_' + method1 + '.csv',
        sep='\t',
        encoding='utf-8')
    file_two = pd.read_csv(
        'data/' + str(year) + '/' + country + '/' + name + '/' + atc + '_' + tech + '_filled_' + method2 + '.csv',
        sep='\t',
        encoding='utf-8')
    return file_one, file_two
