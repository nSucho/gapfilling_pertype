"""
Created on April 2022

@author: Niko Suchowitz
"""
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
    # set 'DateTime' as datetime-type
    original['DateTime'] = pd.to_datetime(original['DateTime'])
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


def plot_filling(original, fedot_fwrd, fedot_bi, kalman_struct, kalman_arima, avg_week, lin_avg_week):
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
    :param avg_week:
    :type avg_week:
    :param lin_avg_week:
    :type lin_avg_week:
    :return:
    :rtype:
    """
    # TODO: first sample to month then plot all into same plot with different colours
    #   still to close to plot properly, not the effect i hope for
    #   sum or mean? sum probably bigger difference

    # reshape the data to monthly for overview-able plots
    original['DateTime'] = pd.to_datetime(original['DateTime'])
    original_monthly = original.resample('M', on='DateTime').mean()
    fedot_fwrd['DateTime'] = pd.to_datetime(fedot_fwrd['DateTime'])
    fedot_fwrd_monthly = fedot_fwrd.resample('M', on='DateTime').mean()
    fedot_bi['DateTime'] = pd.to_datetime(fedot_bi['DateTime'])
    fedot_bi_monthly = fedot_bi.resample('M', on='DateTime').mean()
    kalman_struct['DateTime'] = pd.to_datetime(kalman_struct['DateTime'])
    kalman_struct_monthly = kalman_struct.resample('M', on='DateTime').mean()
    kalman_arima['DateTime'] = pd.to_datetime(kalman_arima['DateTime'])
    kalman_arima_monthly = kalman_arima.resample('M', on='DateTime').mean()
    avg_week['DateTime'] = pd.to_datetime(avg_week['DateTime'])
    avg_week_monthly = avg_week.resample('M', on='DateTime').mean()
    lin_avg_week['DateTime'] = pd.to_datetime(lin_avg_week['DateTime'])
    lin_avg_week_monthly = lin_avg_week.resample('M', on='DateTime').mean()

    # plot
    plt.figure(figsize=(24, 10))
    plt.xlabel('Comparison of XX and the original')

    ax1 = original_monthly['ActualGenerationOutput'].plot(color='blue', grid=True, label='Original', linewidth=4)
    ax2 = fedot_bi_monthly['ActualGenerationOutput'].plot(color='red', grid=True, alpha=1,
                                                            secondary_y=True, label='FEDOT Fwrd')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()

    plt.legend(h1 + h2, l1 + l2, loc=2)
    plt.show()

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
