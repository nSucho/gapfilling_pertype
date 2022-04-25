"""
Created on April 2022

@author: Niko Suchowitz
"""
import os
import glob
import pandas as pd
import gap_filling_aux

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
