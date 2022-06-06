"""
Created on June 2022

@author: Niko Suchowitz
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter


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
    # TODO: standardisierung/ z-transformation oder difference between original und jeweiligen plot

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
    """ fedot plot(x axis looks shit
    plt.plot(time_series, c='blue', alpha=0.4, label='Actual values in the gaps')
    plt.plot(without_gap_poly_1, c='red', alpha=0.8, label='Local polynomial')
    plt.plot(without_gap_poly_2, c='orange', alpha=0.8, label='Batch polynomial')
    plt.plot(without_gap_linear, c='green', alpha=0.8, label='Linear interpolation')
    plt.plot(masked_array, c='blue', alpha=1.0, linewidth=2)
    plt.ylabel('Sea level, m', fontsize=14)
    plt.xlabel('Time index', fontsize=14)
    plt.legend(fontsize=14)
    plt.grid()
    plt.show()
    """
    """second plot with proper x-axis
    plt.figure(figsize=(24, 10))
    plt.xlabel('Comparison of XX and the original')

    ax1 = original_monthly['ActualGenerationOutput'].plot(color='blue', grid=True, label='Original', linewidth=4)
    ax2 = fedot_bi_monthly['ActualGenerationOutput'].plot(color='red', grid=True, alpha=1,
                                                          secondary_y=True, label='FEDOT Fwrd')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()

    plt.legend(h1 + h2, l1 + l2, loc=2)
    plt.show()
    """
    # calc the diff
    difference_fedot_fwrd = substract(original['ActualGenerationOutput'], fedot_fwrd['ActualGenerationOutput'])
    difference_fedot_bi = substract(original['ActualGenerationOutput'], fedot_bi['ActualGenerationOutput'])

    # smoothed
    sal_fwrd = savitzky_golay(difference_fedot_fwrd.to_numpy())
    sal_bi = savitzky_golay(difference_fedot_bi.to_numpy())

    # stand
    nice_ass_1 = standard(difference_fedot_fwrd)
    nice_ass_2 = standard(difference_fedot_bi)
    plt.plot(nice_ass_1, c='blue')
    plt.plot(nice_ass_2, c='red')

    #plt.plot(difference_fedot_fwrd, c='blue', label='Actual values in the gaps')
    #plt.plot(difference_fedot_bi, c='red', label='Local polynomial')
    #plt.show()
    #plt.plot(sal_fwrd, c='orange', label='Batch polynomial')
    #plt.plot(sal_bi, c='green', label='Linear interpolation')
    plt.show()

# TODO: farben für farbenblinde(muster rein), abstände zw den 3 methoden
def plot_validation(avg_week, lin_avg_week, fedot_fwrd, fedot_bi, kalman_struct, kalman_arima):
    """

    :param avg_week:
    :type avg_week:
    :param lin_avg_week:
    :type lin_avg_week:
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
    # mae
    x = np.arange(1)
    # width of the  bars
    width = 0.2
    # plot
    plt.bar(x - 0.5, avg_week[0], width, color='#ADD8E6')
    plt.bar(x - 0.3, lin_avg_week[0], width, color='#00008B')
    plt.bar(x - 0.1, fedot_fwrd[0], width, color='#F08080')
    plt.bar(x + 0.1, fedot_bi[0], width, color='#8B0000')
    plt.bar(x + 0.3, kalman_struct[0], width, color='#90EE90')
    plt.bar(x + 0.5, kalman_arima[0], width, color='#006400')
    plt.xticks(x, ['Mean Average Error'])
    #plt.xlabel("Validation")
    plt.ylabel("Scores")
    # each dict one coloumn
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.title("Mean Average Error")
    plt.show()


    # rmse
    x = np.arange(1)
    # width of the  bars
    width = 0.2
    # plot
    plt.bar(x - 0.5, avg_week[1], width, color='#ADD8E6')
    plt.bar(x - 0.3, lin_avg_week[1], width, color='#00008B')
    plt.bar(x - 0.1, fedot_fwrd[1], width, color='#F08080')
    plt.bar(x + 0.1, fedot_bi[1], width, color='#8B0000')
    plt.bar(x + 0.3, kalman_struct[1], width, color='#90EE90')
    plt.bar(x + 0.5, kalman_arima[1], width, color='#006400')
    plt.xticks(x, ['Root Mean Squared Error'])
    #plt.xlabel("Validation")
    plt.ylabel("Scores")
    # each dict one coloumn
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.title("Root Mean Squared Error")
    plt.show()

    # r^2
    x = np.arange(1)
    # width of the  bars
    width = 0.2
    # plot
    plt.bar(x - 0.5, avg_week[2], width, color='#ADD8E6')
    plt.bar(x - 0.3, lin_avg_week[2], width, color='#00008B')
    plt.bar(x - 0.1, fedot_fwrd[2], width, color='#F08080')
    plt.bar(x + 0.1, fedot_bi[2], width, color='#8B0000')
    plt.bar(x + 0.3, kalman_struct[2], width, color='#90EE90')
    plt.bar(x + 0.5, kalman_arima[2], width, color='#006400')
    plt.xticks(x, ['R^2'])
    #plt.xlabel("Validation")
    plt.ylabel("Scores")
    # each dict one coloumn
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.title("R^2")
    plt.show()


def substract(original_series, second_series):
    """"""
    diff = original_series.sub(second_series)
    return diff


def savitzky_golay(ndarray):
    """
    https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter
    :param ndarray:
    :type ndarray:
    :return:
    :rtype:
    """
    yhat = savgol_filter(ndarray, 51, 3)
    return yhat


# TODO: wie wichtig standartisierung
def standard(array1):
    """"""
    x = (array1 - array1.mean()) / array1.std()
    return x
