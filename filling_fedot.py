"""
Created on January 2021

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


def readin_fedot(country, year, areatypecode, technology):
	""""""
	file_df = pd.read_csv('data/'+str(year)+'/'+country+'/'+str(year)+'_'+areatypecode+'_'+technology+'.csv',
						  sep='\t', encoding='utf-8')
	fedot_method(file_df, country, year, areatypecode, technology)


def fedot_method(data_w_nan, country, year, atc, tech):
	"""
	The autoML solution fedot
	:param data_w_nan: the data with gaps (NaN) to fill
	:param country:
	:param year:
	:param atc:
	:param tech:
	:return: the data with filled gaps (NaN)
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

	# start time to check how long FEDOT was running
	start_time = time.time()

	# Filling in the gaps
	without_gap_forward = model_gapfiller.forward_filling(time_series)
	without_gap_bidirect = model_gapfiller.forward_inverse_filling(time_series)

	#stop time to check how long FEDOT was running
	end_time = time.time()
	time_lapsed = end_time-start_time
	time_convert(time_lapsed)

	#first check if folder exists
	isExist = os.path.exists('data/'+str(year)+'/'+country+'/fedot')
	if not isExist:
		os.makedirs('data/'+str(year)+'/'+country+'/fedot')

	# combine filled values with date and time again
	df_forward = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gap_forward)], axis=1)
	df_bidirect = pd.concat([df_w_nan_copy['DateTime'], pd.Series(without_gap_bidirect)], axis=1)
	# save the combined df as csv
	# TODO: saves strange, see files
	pd.DataFrame(df_forward).to_csv('data/'+str(year)+'/'+country+'/fedot/'+atc+'_'+tech+'_filled_forward.csv',
											 sep='\t', encoding='utf-8', index=False, header=['DateTime', 'ActualGenerationOutput'])
	pd.DataFrame(df_bidirect).to_csv('data/'+str(year)+'/'+country+'/fedot/'+atc+'_'+tech+'_filled_bidirect.csv',
											  sep='\t', encoding='utf-8', index=False, header=['DateTime', 'ActualGenerationOutput'])

	#return the filled gaps
	#return without_gap_forward, without_gap_bidirect


def get_simple_ridge_pipeline():
	"""
	Function for creating pipeline
	:return: the pipeline
	"""
	node_lagged = PrimaryNode('lagged')
	node_lagged.custom_params = {'window_size': 200}

	node_final = SecondaryNode('ridge', nodes_from=[node_lagged])
	pipeline = Pipeline(node_final)

	return pipeline


def time_convert(sec):
	"""
	converts the time from seconds to minutes and hours
	:param sec: time passed in seconds
	:return:
	"""
	mins = sec // 60
	secs = sec % 60
	hours = mins // 60
	mins = mins % 60

	print("Time needed for FEDOT = {0}:{1}:{2}".format(int(hours), int(mins), int(secs)))
