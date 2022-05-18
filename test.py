"""
Created on April 2022

@author: Niko Suchowitz
"""
import readin_aux
import gap_finder
import glob
import time
from csv import *
import pandas as pd
import pathlib


def main():
	"""

	:return:
	"""
	# start time to check how long program was running
	start_time = time.time()

	countries = ['IE_SEM']
	year = '2021'

	# reset the csv file
	with open("countries_w_gaps.csv", "w") as csvfile:
		# create a dict_writer object with the needed attributes
		writer_obj = writer(csvfile, delimiter='\t')
		# write the header into the csv
		writer_obj.writerow(['Month', 'Country', 'Technology', 'AreaTypeCode', 'MissingPercentage'])

	# read in all the monthly csv-files of this country
	files = glob.glob('original_data/' + year + '/' + year + '_??_AggregatedGenerationPerType_16.1.B_C.csv',
					  recursive=False)
	files.sort()

	for file in files:
		# get the string of the month from the file-names
		df_path = pathlib.PurePath(file).parts[2]
		month = df_path[5:7]

		# TODO: comment what is done here
		file_df = pd.read_csv(file, sep='\t', encoding='utf-8')
		file_df["DateTime"] = pd.to_datetime(file_df["DateTime"])
		file_df.sort_values(by='DateTime', inplace=True)
		file_df = file_df.reset_index(drop=True)
		# drop unnecesary coloms
		file_df = file_df.loc[:, ['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput']]

		# create list for all countries and save the list
		#countries = readin_aux.list_countries(file_df)
		# if the list need to be checked for debug
		# with open("country_list.txt", "w") as file_object:
		#    file_object.write(str(countries))
		#    file_object.write("\n")
		#    file_object.write("Amount of Countries: " + str(len(countries)))

		# create list for all AreaTypeCodes and save the list
		atcodes = readin_aux.list_areatypecode(file_df)
		# if the list need to be checked for debug
		# with open("areatypecode_list.txt", "w") as file_object:
		#    file_object.write(str(atcodes))
		#    file_object.write("\n")
		#    file_object.write("Amount of AreaTypeCodes: " + str(len(atcodes)))

		# create list for all technologies and save the list
		technologies = readin_aux.list_technologies(file_df)
		# if the list need to be checked for debug
		# with open("technology_list.txt", "w") as file_object:
		#    file_object.write(str(technologies))
		#    file_object.write("\n")
		#    file_object.write("Amount of technologies: "+str(len(technologies)))

		# find all gaps for each technologie per country
		for atcode in atcodes:
			for technology in technologies:
				for country in countries:
					gap_finder.checkForGaps(file_df, atcode, country, technology, month, year)

	# stop time to check how long program was running
	end_time = time.time()
	time_lapsed = end_time - start_time
	readin_aux.time_convert(time_lapsed)


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
	# for col in df.columns:
	#	if col == 'ActualGenerationOutput':
	#		df.loc[df.sample(frac=0.05).index, col] = np.nan
	df = df.drop(df.sample(frac=.6).index)

	# save with the gaps inserted
	df.to_csv('data/dropped_' + country + '/' + atc + '_' + technology + '_dropped.csv',
			  sep='\t', encoding='utf-8', index=False,
			  header=['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput'])

	return df


if __name__ == '__main__':
	main()
