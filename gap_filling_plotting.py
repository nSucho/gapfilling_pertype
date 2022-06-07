"""
Created on June 2022

@author: Niko Suchowitz
"""
import matplotlib.pyplot as plt
import numpy as np

# TODO: check if folder plots exists
def plot_filling(original, fedot_fwrd, fedot_bi, kalman_struct, kalman_arima, avg_week, lin_avg_week):
    """
    creates wonderful plots to visualize the results
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

    # get the difference and standardize it
    difference_avg_week = substract(original['ActualGenerationOutput'], avg_week['ActualGenerationOutput'])
    stand_avg_week = standard(difference_avg_week)
    difference_lin_avg_week = substract(original['ActualGenerationOutput'], lin_avg_week['ActualGenerationOutput'])
    stand_lin_avg_week = standard(difference_lin_avg_week)
    difference_fedot_fwrd = substract(original['ActualGenerationOutput'], fedot_fwrd['ActualGenerationOutput'])
    stand_fedot_fwrd = standard(difference_fedot_fwrd)
    difference_fedot_bi = substract(original['ActualGenerationOutput'], fedot_bi['ActualGenerationOutput'])
    stand_fedot_bi = standard(difference_fedot_bi)
    difference_kalman_struct = substract(original['ActualGenerationOutput'], kalman_struct['ActualGenerationOutput'])
    stand_kalman_struct = standard(difference_kalman_struct)
    difference_kalman_arima = substract(original['ActualGenerationOutput'], kalman_arima['ActualGenerationOutput'])
    stand_kalman_arima = standard(difference_kalman_arima)

    # plot the difference
    plt.plot(difference_avg_week, color='#377eb8', label='Actual values in the gaps')
    plt.plot(difference_lin_avg_week, color='#ff7f00', label='Local polynomial')
    plt.plot(difference_fedot_fwrd, color='#999999', label='Actual values in the gaps')
    plt.plot(difference_fedot_bi, color='#f781bf', label='Local polynomial')
    plt.plot(difference_kalman_struct, color='#e41a1c', label='Actual values in the gaps')
    plt.plot(difference_kalman_arima, color='#dede00', label='Local polynomial')
    plt.xlabel("Time Index")
    plt.ylabel("Values")
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.savefig('plots/differences.png', bbox_inches='tight')
    #plt.show()
    plt.close()

    # plot the stand
    plt.plot(stand_avg_week, color='#377eb8', label='Actual values in the gaps')
    plt.plot(stand_lin_avg_week, color='#ff7f00', label='Local polynomial')
    plt.plot(stand_fedot_fwrd, color='#999999', label='Actual values in the gaps')
    plt.plot(stand_fedot_bi, color='#f781bf', label='Local polynomial')
    plt.plot(stand_kalman_struct, color='#e41a1c', label='Actual values in the gaps')
    plt.plot(stand_kalman_arima, color='#dede00', label='Local polynomial')
    plt.xlabel("Time Index")
    plt.ylabel("Values")
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.savefig('plots/stand.png', bbox_inches='tight')
    #plt.show()
    plt.close()


# TODO: change xticks
def plot_validation(avg_week, lin_avg_week, fedot_fwrd, fedot_bi, kalman_struct, kalman_arima):
    """
    creates bar-plots for the visualization of the validation
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
    plt.bar(x - 0.6, avg_week[0], width, color='#377eb8', hatch='/')
    plt.bar(x - 0.4, lin_avg_week[0], width, color='#ff7f00', hatch='\\')
    plt.bar(x - 0.1, fedot_fwrd[0], width, color='#999999', hatch='.')
    plt.bar(x + 0.1, fedot_bi[0], width, color='#f781bf', hatch='o')
    plt.bar(x + 0.4, kalman_struct[0], width, color='#e41a1c', hatch='+')
    plt.bar(x + 0.6, kalman_arima[0], width, color='#dede00', hatch='x')
    plt.xticks(x, ['Mean Average Error'])
    #plt.xlabel("Validation")
    plt.ylabel("Scores")
    # each method one bar
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.title("Mean Average Error")
    plt.savefig('plots/mae.png', bbox_inches='tight')
    #plt.show()
    plt.close()

    # rmse
    x = np.arange(1)
    # width of the  bars
    width = 0.2
    # plot
    plt.bar(x - 0.6, avg_week[1], width, color='#377eb8', hatch='/')
    plt.bar(x - 0.4, lin_avg_week[1], width, color='#ff7f00', hatch='\\')
    plt.bar(x - 0.1, fedot_fwrd[1], width, color='#999999', hatch='.')
    plt.bar(x + 0.1, fedot_bi[1], width, color='#f781bf', hatch='o')
    plt.bar(x + 0.4, kalman_struct[1], width, color='#e41a1c', hatch='+')
    plt.bar(x + 0.6, kalman_arima[1], width, color='#dede00', hatch='x')
    plt.xticks(x, ['Root Mean Squared Error'])
    #plt.xlabel("Validation")
    plt.ylabel("Scores")
    # each method one bar
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.title("Root Mean Squared Error")
    plt.savefig('plots/rmse.png', bbox_inches='tight')
    #plt.show()
    plt.close()

    # r^2
    x = np.arange(1)
    # width of the  bars
    width = 0.2
    # plot
    plt.bar(x - 0.6, avg_week[2], width, color='#377eb8', hatch='/')
    plt.bar(x - 0.4, lin_avg_week[2], width, color='#ff7f00', hatch='\\')
    plt.bar(x - 0.1, fedot_fwrd[2], width, color='#999999', hatch='.')
    plt.bar(x + 0.1, fedot_bi[2], width, color='#f781bf', hatch='o')
    plt.bar(x + 0.4, kalman_struct[2], width, color='#e41a1c', hatch='+')
    plt.bar(x + 0.6, kalman_arima[2], width, color='#dede00', hatch='x')
    plt.xticks(x, ['R^2'])
    #plt.xlabel("Validation")
    plt.ylabel("Scores")
    # each method one bar
    plt.legend(["Average week", "Linear average week", "FEDOT forward", "FEDOT bidirect", "Kalman structTS",
                "Kalman arima"])
    plt.title("R^2")
    plt.savefig('plots/r2.png', bbox_inches='tight')
    #plt.show()
    plt.close()


def substract(original_series, second_series):
    """
    substracts the filled series from the original
    :param original_series:
    :type original_series:
    :param second_series:
    :type second_series:
    :return:
    :rtype:
    """
    diff = original_series.sub(second_series)
    return diff


# TODO: wie wichtig standartisierung
def standard(array1):
    """

    :param array1:
    :type array1:
    :return:
    :rtype:
    """
    x = (array1 - array1.mean()) / array1.std()
    return x
