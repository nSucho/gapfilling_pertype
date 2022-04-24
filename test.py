"""
Created on April 2022

@author: Niko Suchowitz
"""
import pandas as pd
from gap_finder import *
from auxiliary_methods import *
import numpy as np
import time
np.random.seed(15)


def main():
	"""

	:return:
	"""
	# start time to check how long program was running
	start_time = time.time()

	countries = ['AT', 'IE_SEM']
	atcodes = ['CTA', 'BZN']
	technologies = ['Fossil Gas', 'Solar']
	year = '2021'


	file_df = pd.read_csv('original_data/'+year+'/'+year+'_01_AggregatedGenerationPerType_16.1.B_C.csv',
	                      sep='\t', encoding='utf-8')
	file_df = file_df.loc[:, ['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput']]

	# reset the csv file
	with open("countries_w_gaps.csv", "w") as csvfile:
		# create a dict_writer object with the needed attributes
		writer_obj = writer(csvfile, delimiter='\t')
		# write the header into the csv
		writer_obj.writerow(['Month', 'Country', 'Technology', 'AreaTypeCode', 'MissingPercentage'])

	# loop
	for atc in atcodes:
		for technology in technologies:
			for country in countries:
				file_df_copy = file_df.loc[(file_df["MapCode"] == country) & (file_df["ProductionType"] == technology) &
				                         (file_df["AreaTypeCode"] == atc)]
				file_df_copy["DateTime"] = pd.to_datetime(file_df_copy["DateTime"])
				file_df_copy.sort_values(by='DateTime', inplace=True)
				file_df_copy = file_df_copy.reset_index(drop=True)

				create_path('data/dropped_'+country+'/'+atc)
				# save with the gaps inserted
				file_df_copy.to_csv('data/dropped_'+country+'/'+atc+'_'+technology+'.csv',
				               sep='\t', encoding='utf-8', index=False,
				               header=['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput'])

				gapped_df = create_gaps(file_df_copy, country, atc, technology)

				checkForGaps(gapped_df, atc, country, technology, month=1, year=2021)
	#stop time to check how long program was running
	end_time = time.time()
	time_lapsed = end_time-start_time
	time_convert(time_lapsed)


def create_gaps(data_without_gaps, country, atc, technology):
	"""
	creates a df with 'frac' amount of gaps (as np.nan) from the original

	:param data_without_gaps: original df without gaps
	:param country:
	:param atc:
	:param technology:
	:return: df with gaps
	"""
	# create copy so we do not change original
	df = data_without_gaps.copy()

	# randomly set frac-amount of the data to np.nan
	# frac = 0.1 means 10% of the data will be gaps
	#for col in df.columns:
	#	if col == 'ActualGenerationOutput':
	#		df.loc[df.sample(frac=0.05).index, col] = np.nan
	df = df.drop(df.sample(frac=.6).index)

	# save with the gaps inserted
	df.to_csv('data/dropped_'+country+'/'+atc+'_'+technology+'_dropped.csv',
	          sep='\t', encoding='utf-8', index=False,
	          header=['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput'])

	return df


if __name__ == '__main__':
	main()
