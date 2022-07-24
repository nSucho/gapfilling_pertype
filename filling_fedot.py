"""
Created on May 2022

@author: Niko Suchowitz
"""
import numpy as np
import os
# Pipeline and nodes
import pandas as pd
from fedot.core.pipelines.pipeline import Pipeline
from fedot.core.pipelines.node import PrimaryNode, SecondaryNode
from fedot.utilities.ts_gapfilling import ModelGapFiller


# can still not handle gaps in first 7 segments
def fedot_frwd_bi(data_w_nan, country, year, atc, tech, datatype, val_col, header, fedot_window):
    """

    :param data_w_nan:
    :type data_w_nan:
    :param country:
    :type country:
    :param year:
    :type year:
    :param atc:
    :type atc:
    :param tech:
    :type tech:
    :param datatype:
    :type datatype:
    :param val_col:
    :type val_col:
    :param header:
    :type header:
    :param fedot_window:
    :type fedot_window:
    :return:
    :rtype:
    """
    # copy the df so we do not change the original
    df_w_nan_copy = data_w_nan.copy()

    # fill the nan with '-100' so fedot can work with it
    df_w_nan_copy = df_w_nan_copy.fillna(-100)

    # Got univariate time series as numpy array
    time_series = np.array(df_w_nan_copy[val_col])

    # create a pipeline and defines the values which count as gaps
    pipeline = get_simple_ridge_pipeline(fedot_window)
    model_gapfiller = ModelGapFiller(gap_value=-100.0,
                                     pipeline=pipeline)

    # ----------
    # Filling in the gaps
    # ----------
    without_gap_forward = model_gapfiller.forward_filling(time_series)
    without_gap_bidirect = model_gapfiller.forward_inverse_filling(time_series)

    # first check if folder exists to save data in
    isExist = os.path.exists('data/' + datatype + '/' + str(year) + '/' + country + '/fedot')
    if not isExist:
        os.makedirs('data/' + datatype + '/' + str(year) + '/' + country + '/fedot')

    # combine filled values with date and time again
    df_forward = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gap_forward)], axis=1)
    #df_bidirect = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gap_bidirect)], axis=1)
    # set header
    df_forward.columns = header
    #df_bidirect.columns = header

    # save the combined df as csv
    pd.DataFrame(df_forward).to_csv('data/' + datatype + '/' + str(year) + '/' + country + '/fedot/' + atc + '_' + tech
                                    + '_filled_forward.csv', sep='\t', encoding='utf-8', index=False, header=header)
    #pd.DataFrame(df_bidirect).to_csv('data/' + datatype + '/' + str(year) + '/' + country + '/fedot/' + atc + '_' + tech
    #                                 + '_filled_bidirect.csv', sep='\t', encoding='utf-8', index=False, header=header)

    #return df_forward, df_bidirect
    return df_forward


def get_simple_ridge_pipeline(fedot_window):
    """

    :param fedot_window: size of the sliding window
    :type fedot_window:
    :return:
    :rtype:
    """
    node_lagged = PrimaryNode('lagged')
    node_lagged.custom_params = {'window_size': fedot_window}

    node_final = SecondaryNode('ridge', nodes_from=[node_lagged])
    pipeline = Pipeline(node_final)

    return pipeline

