"""
Created on May 2022

@author: Niko Suchowitz
"""

# TODO: implement better pipeline
import time
import numpy as np
import os
# Pipeline and nodes
import pandas as pd
from fedot.core.pipelines.pipeline import Pipeline
from fedot.core.pipelines.node import PrimaryNode, SecondaryNode
from fedot.utilities.ts_gapfilling import ModelGapFiller


def fedot_frwd_bi(data_w_nan, country, year, atc, tech):
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
    :return:
    :rtype:
    """
    # copy the df so we do not change the original
    df_w_nan_copy = data_w_nan.copy()

    # fill the nan with '-100' so fedot can work with it
    df_w_nan_copy = df_w_nan_copy.fillna(-100)

    # Got univariate time series as numpy array
    time_series = np.array(df_w_nan_copy['ActualGenerationOutput'])

    # create a pipeline and defines the values which count as gaps
    pipeline = get_simple_ridge_pipeline()
    model_gapfiller = ModelGapFiller(gap_value=-100.0,
                                     pipeline=pipeline)

    # Filling in the gaps
    # TODO: filled with minus
    without_gap_forward = model_gapfiller.forward_filling(time_series)
    without_gap_bidirect = model_gapfiller.forward_inverse_filling(time_series)

    # first check if folder exists to save data in
    isExist = os.path.exists('data/' + str(year) + '/' + country + '/fedot')
    if not isExist:
        os.makedirs('data/' + str(year) + '/' + country + '/fedot')

    # combine filled values with date and time again
    df_forward = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gap_forward)], axis=1)
    df_bidirect = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gap_bidirect)], axis=1)
    # set header
    df_forward.columns = ["DateTime", "ActualGenerationOutput"]
    df_bidirect.columns = ["DateTime", "ActualGenerationOutput"]

    # save the combined df as csv
    pd.DataFrame(df_forward).to_csv(
        'data/' + str(year) + '/' + country + '/fedot/' + atc + '_' + tech + '_filled_forward.csv',
        sep='\t', encoding='utf-8', index=False, header=['DateTime', 'ActualGenerationOutput'])
    pd.DataFrame(df_bidirect).to_csv(
        'data/' + str(year) + '/' + country + '/fedot/' + atc + '_' + tech + '_filled_bidirect.csv',
        sep='\t', encoding='utf-8', index=False, header=['DateTime', 'ActualGenerationOutput'])

    return df_forward, df_bidirect


def get_simple_ridge_pipeline():
    """

    :return:
    :rtype:
    """
    node_lagged = PrimaryNode('lagged')
    node_lagged.custom_params = {'window_size': 200}

    node_final = SecondaryNode('ridge', nodes_from=[node_lagged])
    pipeline = Pipeline(node_final)

    return pipeline


def fedot_ridge_composite(data_w_nan, country, year, atc, tech):
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
    :return:
    :rtype:
    """
    # copy the df so we do not change the original
    df_w_nan_copy = data_w_nan.copy()

    # fill the nan with '-100' so fedot can work with it
    df_w_nan_copy = df_w_nan_copy.fillna(-100)

    df_w_nan_copy['DateTime'] = pd.to_datetime(df_w_nan_copy['DateTime'])

    # Filling in gaps based on inverted ridge regression model
    ridge_pipeline = get_simple_pipeline()
    ridge_gapfiller = ModelGapFiller(gap_value=-100.0,
                                     pipeline=ridge_pipeline)
    with_gap_array = np.array(df_w_nan_copy['ActualGenerationOutput'])
    without_gap_arr_ridge = ridge_gapfiller.forward_inverse_filling(with_gap_array)

    # Filling in gaps based on a pipeline of 5 models
    composite_pipeline = get_composite_pipeline()
    composite_gapfiller = ModelGapFiller(gap_value=-100.0,
                                         pipeline=composite_pipeline)
    without_gap_composite = composite_gapfiller.forward_filling(with_gap_array)

    df_ridge = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gap_arr_ridge)], axis=1)
    df_composite = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gap_composite)], axis=1)

    df_ridge.columns = ["DateTime", "ActualGenerationOutput"]
    df_composite.columns = ["DateTime", "ActualGenerationOutput"]

    # save the combined df as csv
    pd.DataFrame(df_ridge).to_csv(
        'data/' + str(year) + '/' + country + '/fedot/' + atc + '_' + tech + '_filled_ridge.csv',
        sep='\t', encoding='utf-8', index=False, header=['DateTime', 'ActualGenerationOutput'])
    pd.DataFrame(df_composite).to_csv(
        'data/' + str(year) + '/' + country + '/fedot/' + atc + '_' + tech + '_filled_composite.csv',
        sep='\t', encoding='utf-8', index=False, header=['DateTime', 'ActualGenerationOutput'])

    return df_ridge, df_composite


def get_simple_pipeline():
    """ Function returns simple pipeline """
    node_lagged = PrimaryNode('lagged')
    node_lagged.custom_params = {'window_size': 200}
    node_ridge = SecondaryNode('ridge', nodes_from=[node_lagged])
    ridge_pipeline = Pipeline(node_ridge)
    return ridge_pipeline


def get_composite_pipeline():
    """
    The function returns prepared pipeline of 5 models
    :return: Pipeline object
    """

    node_1 = PrimaryNode('lagged')
    node_1.custom_params = {'window_size': 200}
    node_2 = PrimaryNode('lagged')
    node_2.custom_params = {'window_size': 100}
    node_linear_1 = SecondaryNode('linear', nodes_from=[node_1])
    node_linear_2 = SecondaryNode('linear', nodes_from=[node_2])

    node_final = SecondaryNode('ridge', nodes_from=[node_linear_1,
                                                    node_linear_2])
    pipeline = Pipeline(node_final)
    return pipeline
