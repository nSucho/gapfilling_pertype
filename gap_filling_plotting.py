"""
Created on June 2022

@author: Niko Suchowitz
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd


def plot_filling(original, fedot_fwrd, fedot_bi, kalman_struct, kalman_arima, avg_week, lin_avg_week, val_col, datatype,
                 year, country, tech, fedot_window, amount_gaps):
    """
    plots the difference and standardizing of the original data to the predicted one
    :param original: original data without gaps
    :type original: dataframe
    :param fedot_fwrd: dataframe with predicted values of fedot forward
    :type fedot_fwrd: dataframe
    :param fedot_bi: dataframe with predicted values of fedot bidirect
    :type fedot_bi: dataframe
    :param kalman_struct: dataframe with predicted values of kalman structts
    :type kalman_struct: dataframe
    :param kalman_arima: dataframe with predicted values of kalman auto.arima
    :type kalman_arima: dataframe
    :param avg_week: dataframe with predicted values of average week
    :type avg_week: dataframe
    :param lin_avg_week: dataframe with predicted values of linear average week
    :type lin_avg_week: dataframe
    :param val_col: header of the important column with the values
    :type val_col: string
    :param datatype: type of the data
    :type datatype: string
    :param year: year of the data
    :type year: string
    :param country: country code of the original data
    :type country: string
    :param tech: technology of the original data
    :type tech: string
    :param fedot_window: window size for the fedot pipeline
    :type fedot_window: int
    :param amount_gaps: amount of the gaps inserted
    :type amount_gaps: float
    :return:
    :rtype:
    """
    # create datetime-series
    # get the difference and standardize it
    difference_avg_week = substract(original[val_col], avg_week[val_col])
    stand_avg_week = standardizing(difference_avg_week)
    difference_lin_avg_week = substract(original[val_col], lin_avg_week[val_col])
    stand_lin_avg_week = standardizing(difference_lin_avg_week)
    difference_fedot_fwrd = substract(original[val_col], fedot_fwrd[val_col])
    stand_fedot_fwrd = standardizing(difference_fedot_fwrd)
    difference_fedot_bi = substract(original[val_col], fedot_bi[val_col])
    stand_fedot_bi = standardizing(difference_fedot_bi)
    difference_kalman_struct = substract(original[val_col], kalman_struct[val_col])
    stand_kalman_struct = standardizing(difference_kalman_struct)
    difference_kalman_arima = substract(original[val_col], kalman_arima[val_col])
    stand_kalman_arima = standardizing(difference_kalman_arima)

    # ----------
    # plot the difference
    # ----------
    plt.plot(original['DateTime'], difference_avg_week, color='#377eb8', label='Actual values in the gaps')
    plt.plot(original['DateTime'], difference_lin_avg_week, color='#ff7f00', label='Local polynomial')
    plt.plot(original['DateTime'], difference_fedot_fwrd, color='#999999', label='Actual values in the gaps')
    plt.plot(original['DateTime'], difference_fedot_bi, color='#f781bf', label='Local polynomial')
    plt.plot(original['DateTime'], difference_kalman_struct, color='#e41a1c', label='Actual values in the gaps')
    plt.plot(original['DateTime'], difference_kalman_arima, color='#dede00', label='Local polynomial')
    plt.xticks(rotation=30, ha='right')
    plt.xlabel("Date Time")
    plt.ylabel("Difference \'original\'-value to \'method\'-value")
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.title('Country: ' + country + ', Technology: ' + tech + ', Year: ' + year)
    plt.tight_layout()
    plt.savefig('plots/' + datatype + '/' + year + '/' + country + '_' + tech + '_' + str(amount_gaps) + '_' +
                str(fedot_window) + '_' + 'difference.png', bbox_inches='tight')

    #plt.show()
    plt.close()

    # ----------
    # plot the standardizing
    # ----------
    plt.plot(original['DateTime'], stand_avg_week, color='#377eb8', label='Actual values in the gaps')
    plt.plot(original['DateTime'], stand_lin_avg_week, color='#ff7f00', label='Local polynomial')
    plt.plot(original['DateTime'], stand_fedot_fwrd, color='#999999', label='Actual values in the gaps')
    plt.plot(original['DateTime'], stand_fedot_bi, color='#f781bf', label='Local polynomial')
    plt.plot(original['DateTime'], stand_kalman_struct, color='#e41a1c', label='Actual values in the gaps')
    plt.plot(original['DateTime'], stand_kalman_arima, color='#dede00', label='Local polynomial')
    plt.xticks(rotation=30, ha='right')
    plt.xlabel("Date Time")
    plt.xlabel("Time Index")
    plt.ylabel("Standardized difference \'original\'-value to \'method\'-value")
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.title('Country: ' + country + ', Technology: ' + tech + ', Year: ' + year)
    plt.tight_layout()
    plt.savefig('plots/' + datatype + '/' + year + '/' + country + '_' + tech + '_' + str(amount_gaps) + '_' +
                str(fedot_window) + '_' + 'stand.png', bbox_inches='tight')
    #plt.show()
    plt.close()


def plot_validation(avg_week, lin_avg_week, fedot_fwrd, fedot_bi, kalman_struct, kalman_arima, datatype, year, country,
                    tech, fedot_window, amount_gaps):
    """
    plot the results of the validation of the predicitons
    :param avg_week: dataframe with predicted values of average week
    :type avg_week: dataframe
    :param lin_avg_week: dataframe with predicted values of linear average week
    :type lin_avg_week: dataframe
    :param fedot_fwrd: dataframe with predicted values of fedot forward
    :type fedot_fwrd: dataframe
    :param fedot_bi: dataframe with predicted values of fedot bidirect
    :type fedot_bi: dataframe
    :param kalman_struct: dataframe with predicted values of kalman structts
    :type kalman_struct: dataframe
    :param kalman_arima: dataframe with predicted values of kalman auto.arima
    :type kalman_arima: dataframe
    :param datatype: type of the data
    :type datatype: string
    :param year: year of the original data
    :type year: string
    :param country: country code of the original data
    :type country: string
    :param tech: technology of the original data
    :type tech: string
    :param fedot_window: window size for the fedot pipeline
    :type fedot_window: int
    :param amount_gaps: amount of gaps inserted into the original dataframe
    :type amount_gaps: float
    :return:
    :rtype:
    """
    # ----------
    # general set up
    # ----------
    methods = ["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
               "Kalman arima"]
    amount_x = np.arange(len(methods))
    # width of the  bars
    width = 0.2
    # color of the bars
    color = ['#377eb8', '#ff7f00', '#999999', '#f781bf', '#e41a1c', '#dede00']
    # pattern of the plots
    hatch = ['/', '\\', '.', 'o', '+', 'x']

    # ----------
    # plot MAE
    # ----------
    y_values = [avg_week[0], lin_avg_week[0], fedot_fwrd[0], fedot_bi[0], kalman_struct[0], kalman_arima[0]]
    bar_plot = plt.bar(amount_x, y_values, color=color, hatch=hatch, width = 0.2)
    plt.xticks(amount_x, methods, rotation=30)
    plt.ylabel("\'Mean Average Error\' -values")
    plt.title('Country: ' + country + ', Technology: ' + tech + ', Year: ' + year)
    # adds the values of the bars on top of it
    add_bar_label(bar_plot, 2)
    # fits the boundaries of the plot, so nothing gets cut off
    plt.tight_layout()
    plt.savefig('plots/' + datatype + '/' + year + '/' + country + '_' + tech + '_' + str(amount_gaps) + '_' +
                str(fedot_window) + '_' + 'mae.png', bbox_inches='tight')
    # plt.show()
    plt.close()

    # ----------
    # plot RMSE
    # ----------
    y_values = [avg_week[1], lin_avg_week[1], fedot_fwrd[1], fedot_bi[1], kalman_struct[1], kalman_arima[1]]
    bar_plot = plt.bar(amount_x, y_values, color=color, hatch=hatch)
    plt.xticks(amount_x, methods, rotation=30)
    plt.ylabel("\'Root Mean Squared Error\' -values")
    plt.title('Country: ' + country + ', Technology: ' + tech + ', Year: ' + year)
    # adds the values of the bars on top of it
    add_bar_label(bar_plot, 2)
    # fits the boundaries of the plot, so nothing gets cut off
    plt.tight_layout()
    plt.savefig('plots/' + datatype + '/' + year + '/' + country + '_' + tech + '_' + str(amount_gaps) + '_' +
                str(fedot_window) + '_' + 'rmse.png', bbox_inches='tight')
    # plt.show()
    plt.close()

    # ----------
    # plot R^2
    # ----------
    y_values = [avg_week[2], lin_avg_week[2], fedot_fwrd[2], fedot_bi[2], kalman_struct[2], kalman_arima[2]]
    bar_plot = plt.bar(amount_x, y_values, color=color, hatch=hatch)
    plt.xticks(amount_x, methods, rotation=30)
    plt.ylabel(u"\'R\u00b2\' -values")
    plt.title('Country: ' + country + ', Technology: ' + tech + ', Year: ' + year)
    # adds the values of the bars on top of it
    add_bar_label(bar_plot, 4)
    # fits the boundaries of the plot, so nothing gets cut off
    plt.tight_layout()
    plt.savefig('plots/' + datatype + '/' + year + '/' + country + '_' + tech + '_' + str(amount_gaps) + '_' +
                str(fedot_window) + '_' + 'r2.png', bbox_inches='tight')
    #plt.show()
    plt.close()


def substract(original_series, second_series):
    """
    substracts the filled series from the original
    :param original_series: values of the original series
    :type original_series: series
    :param second_series: values of the new series
    :type second_series: series
    :return: the difference of the two series
    :rtype: series
    """
    diff = original_series.sub(second_series)
    return diff


def standardizing(array1):
    """
    standardizing the difference of two series
    :param array1: array with the series
    :type array1: array
    :return: array with the standardization
    :rtype: array
    """
    x = (array1 - array1.mean()) / array1.std()
    return x


def add_bar_label(bar_plot, after_dec):
    """
    Adds values on top of the bars
    :param bar_plot:
    :type bar_plot:
    :param after_dec:
    :type after_dec:
    :return:
    :rtype:
    """
    for bar in bar_plot:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height, round(height, after_dec), ha='center', va='bottom')