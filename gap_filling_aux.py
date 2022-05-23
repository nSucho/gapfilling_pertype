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


def validation(original, filled_gaps):
    vali_dict = {'mae': mean_absolute_error(original, filled_gaps),
                 'rmse': np.sqrt(mean_squared_error(original, filled_gaps)), 'r2': r2_score(original, filled_gaps)}

    return vali_dict


def read_in(year, atc, country, tech, create_gaps):
    # read in the file
    original = pd.read_csv('data/' + str(year) + '/' + country + '/' + str(year) + '_' + atc + '_' +
                          tech + '.csv', sep='\t', encoding='utf-8')
    if create_gaps:
        data_w_nan = insert_the_gaps(original)
    return original, data_w_nan


def insert_the_gaps(original):
    # create copy so we do not change original
    original_copy = original.copy()

    # randomly set frac-amount of the data to np.nan
    # frac = 0.1 means 10% of the data will be gaps
    for col in original_copy.columns:
        if col == 'ActualGenerationOutput':
            original_copy.loc[original_copy.sample(frac=0.01).index, col] = np.nan
    return original_copy


# TODO: macht nicht so geiles Zeug
def save_validation(dict):
    for values in dict:
        with open("results.txt", "a") as file_object:
            file_object.write(values+': ' + str(dict[values]))
            file_object.write("\n")


def plot_filling(original, mask, fedot_fwrd, fedot_bi, kalman_struct, kalman_arima):
    # TODO: first sample to month then plot all into same plot with different colours
    plt.plot(original, c='blue', alpha=0.4, label='Actual values in the gaps')
    plt.plot(fedot_fwrd, c='red', alpha=0.8, label='Forward')
    plt.plot(fedot_bi, c='orange', alpha=0.8, label='Bidirect')
    plt.plot(kalman_struct, c='green', alpha=0.8, label='StructTS')
    plt.plot(kalman_arima, c='purple', alpha=0.8, label='Arima')
    plt.plot(mask, c='blue', alpha=1.0, linewidth=2)
    plt.ylabel('Value', fontsize=14)
    plt.xlabel('DateTime', fontsize=14)
    plt.legend(fontsize=14)
    plt.grid()
    plt.show()


# TODO: kick out later
def readin_test(year, country, atc, tech, name, method1, method2):
    # read in the file
    file_one = pd.read_csv('data/'+str(year)+'/'+country+'/'+name+'/'+atc+'_'+tech+'_filled_'+method1+'.csv', sep='\t',
                           encoding='utf-8')
    file_two = pd.read_csv('data/'+str(year)+'/'+country+'/'+name+'/'+atc+'_'+tech+'_filled_'+method2+'.csv', sep='\t',
                           encoding='utf-8')
    return file_one, file_two


# TODO: kick out later
def round(dataframe):
    dataframe["DateTime"] = pd.to_datetime(dataframe["DateTime"])
    dataframe = dataframe.set_index(['DateTime'])
    dataframe['ActualGenerationOutput'] = round(dataframe.resample('M').mean()['ActualGenerationOutput'])
    dataframe.dropna(subset=["ActualGenerationOutput"], inplace=True)
    dataframe.reset_index(inplace=True)

    return dataframe