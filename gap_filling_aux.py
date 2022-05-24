"""
Created on April 2022

@author: Niko Suchowitz
"""
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import rcParams

rcParams['figure.figsize'] = 18, 7
np.random.seed(10)


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
    if create_gaps:
        data_w_nan = insert_the_gaps(original)
    return original, data_w_nan


def insert_the_gaps(original):
    """

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
    vali_dict = {'mae': mean_absolute_error(original, filled_gaps),
                 'rmse': np.sqrt(mean_squared_error(original, filled_gaps)), 'r2': r2_score(original, filled_gaps)}

    return vali_dict


def plot_filling(original, fedot_fwrd, fedot_bi, kalman_struct, kalman_arima):
    """

    :param original:
    :type original:
    :param fedot_fwrd:
    :type fedot_fwrd:
    :param fedot_bi:
    :type fedot_bi:
    :param kalman_struct:
    :type kalman_struct:
    :param kalman_arima:
    :type kalman_arima:
    :return:
    :rtype:
    """
    # TODO: first sample to month then plot all into same plot with different colours
    plt.plot(original, c='blue', alpha=0.4, label='Actual values in the gaps')
    plt.plot(fedot_fwrd, c='red', alpha=0.8, label='Forward')
    plt.plot(fedot_bi, c='orange', alpha=0.8, label='Bidirect')
    plt.plot(kalman_struct, c='green', alpha=0.8, label='StructTS')
    plt.plot(kalman_arima, c='purple', alpha=0.8, label='Arima')
    plt.ylabel('Value', fontsize=14)
    plt.xlabel('DateTime', fontsize=14)
    plt.legend(fontsize=14)
    plt.grid()
    plt.show()


# TODO: kick out later
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
