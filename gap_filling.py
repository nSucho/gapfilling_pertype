"""
Created on April 2022

@author: Niko Suchowitz
"""
import pandas as pd
import filling_fedot
import filling_kalman


def gapfill_main():
    """

    :return:
    """
    # setting the values
    year = '2021'
    areatypecode = 'BZN'
    country = 'IE_SEM'
    technology = 'Fossil Peat'

    # read in the file
    file_df = pd.read_csv('data/' + str(year) + '/' + country + '/' + str(year) + '_' + areatypecode + '_' +
                          technology + '.csv', sep='\t', encoding='utf-8')

    # filling the gaps with fedot
    #fedot_forward, fedot_bidirect = filling_fedot.fedot_method(file_df, country, year, areatypecode, technology)
    # filling the gaps with Kalman-filter
    kalman_structs, kalman_arima = filling_kalman.kalman_method(file_df, country, year, areatypecode, technology)


if __name__ == '__main__':
    gapfill_main()
