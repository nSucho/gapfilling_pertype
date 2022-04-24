"""
Created on April 2022

@author: Niko Suchowitz
"""
import os
import glob
import pandas as pd
import gap_length_analyser

def list_countries(file_df):
	"""

	:param file_df:
	:return: list with countries represented in the files
	"""
	file_copy = file_df.copy()
	# take only the technologies of the country and drop the duplicates
	country_list = list(file_copy['MapCode'].drop_duplicates())
	country_list.sort()

	return country_list


def list_areatypecode(file_df):
	"""

	:param file_df:
	:return: list with countries represented in the files
	"""
	file_copy = file_df.copy()
	# take only the technologies of the country and drop the duplicates
	areatypecode_list = list(file_copy['AreaTypeCode'].drop_duplicates())
	areatypecode_list.sort()

	return areatypecode_list


def list_technologies(file_df):
	"""

	:param file_df:
	:return: list with technologies used to generate electricity
	"""
	file_copy = file_df.copy()
	# take only the technologies of the country and drop the duplicates
	tech_list = file_copy['ProductionType'].drop_duplicates()

	# replace the '/'
	tech_list = list(map(lambda x: x.replace('Fossil Brown coal/Lignite', 'Fossil Brown coal Lignite'), tech_list))
	tech_list.sort()

	return tech_list


def create_path(path):
	"""
	Checks if the path already exists else creates it

	:param path: path of the folder
	:return:
	"""
	isExist = os.path.exists(path)
	if not isExist:
		os.makedirs(path)
		#print("Created the new directory " +path)


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

	print("Time needed for the program = {0}:{1}:{2}".format(int(hours), int(mins), int(secs)))

	with open("runtime.txt", "a") as file_object:
		file_object.write("Time needed for the program = {0}:{1}:{2}".format(int(hours), int(mins), int(secs)))
		file_object.write("\n")


def calc_missing_data(df_to_check):
	"""
	calculates the missing data

	:param df_to_check: the df you want to check for missing data
	:return: missing data in percent
	"""

	missing_data_o = df_to_check['ActualGenerationOutput'].isna().sum()
	missing_percent = (missing_data_o/len(df_to_check.index))*100

	return missing_percent


def unify_year(mapcode_gapfree, year):
	"""
	Creates a df of the whole year from the csv created in unify_monthly

	:param mapcode_gapfree: mapcode of the country
	:param year: year which is wanted
	:return: df of the whole year
	"""
	# read in all the monthly csv-files of this country
	files = glob.glob('data/own_data/ActualTotalLoad_edited/'+mapcode_gapfree+'/'+year+'_??_ActualTotalLoad_6.1.A_'
	                  + mapcode_gapfree+'CTA.csv', recursive=False)
	files.sort()

	# concat to one dataframe and reset index
	df_original = pd.concat([pd.read_csv(file, sep='\t', encoding='utf-8') for file in files])
	df_original["DateTime"] = pd.to_datetime(df_original["DateTime"])
	df_original = df_original.reset_index(drop=True)

	# safe whole year as csv
	df_original.to_csv(
		'data/own_data/ActualTotalLoad_edited/'+mapcode_gapfree+'/'+year+'_'+mapcode_gapfree+'_original.csv',
		sep='\t', encoding='utf-8', index=False,
		header=["DateTime", "ResolutionCode", "AreaCode", "AreaTypeCode", "AreaName",
		        "MapCode", "TotalLoadValue", "UpdateTime"])

	return df_original


def unify_year(year, country, areatypecode, technology):
	"""
	Creates a df of the whole year from the monthly csv

	:param year: year which is wanted
	:param month:
	:param country:
	:param areatypecode:
	:param technology:
	:return: df of the whole year
	"""
	# read in all the monthly csv-files of this country
	files = glob.glob('data/'+str(year)+'/'+country+'/final_sorted_tech/\b([1-9]|1[0-2])\b_'+areatypecode+'_'
			                + technology+'_[w|no]gaps.csv', recursive=False)

	# concat to one dataframe and reset index
	df_year = pd.concat([pd.read_csv(file, sep='\t', encoding='utf-8') for file in files])
	df_year["DateTime"] = pd.to_datetime(df_year["DateTime"])
	df_year = df_year.reset_index(drop=True)

	# safe whole year as csv
	df_year.to_csv(
		'data/'+str(year)+'/'+country+'/'+str(year)+'_'+areatypecode+'_'+technology+'.csv',
		sep='\t', encoding='utf-8', index=False,
		header=["DateTime", "ResolutionCode", "AreaCode", "AreaTypeCode", "AreaName",
		        "MapCode", "TotalLoadValue", "UpdateTime"])

	# list the length of the gaps
	gap_length_analyser.analyze_gap_length(df_year, year, country, areatypecode, technology)
