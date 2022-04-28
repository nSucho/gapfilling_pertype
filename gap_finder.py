"""
Created on April 2022

@author: Niko Suchowitz
"""
from datetime import datetime as dt
from datetime import date
import calendar

import gap_filling_aux
from readin_aux import *
import pandas as pd
import numpy as np
from csv import *

pd.options.mode.chained_assignment = None  # default='warn'


# TODO: overall main?
def checkForGaps(file_df_original, areatypecode, country, technology, month, year):
	"""
	Checks 'file_df_original' for missing entries in the data

	:param file_df_original: the original file
	:param areatypecode: the Area-Type-Code to check
	:param country: the country to check
	:param technology: the technology to check
	:param month: the month of the data
	:param year: the year of the data
	:return:
	"""
	file_df = file_df_original.copy()

	# for saving the gaps-info later
	field_names = ['Month', 'Country', 'Technology', 'AreaTypeCode', 'MissingPercentage']
	# check if neccesary folders exist, else create
	create_path('data/'+str(year)+'/'+country+'/raw_sorted_tech')
	create_path('data/'+str(year)+'/'+country+'/final_sorted_tech')
	create_path('data/'+str(year)+'/'+country+'/gaplists_per_tech')

	# some (country, ATC, Technology)-combinations do not exist, so catch the error for them
	try:
		# only take rows into 'act_gen_df' which are equal to our wanted attributes
		act_gen_df = file_df.loc[(file_df["MapCode"] == country) & (file_df["ProductionType"] == technology) &
		                         (file_df["AreaTypeCode"] == areatypecode)]
		# not needed: act_gen_df["DateTime"] = pd.to_datetime(act_gen_df["DateTime"])
		# sort by DateTime-column
		# not needed: act_gen_df.sort_values(by='DateTime', inplace=True)

		# if the 'DateTime' is not in hourly steps, we downsample to hours
		# first we have to set the 'DateTime' as index
		act_gen_df = act_gen_df.set_index(['DateTime'])
		# now resample
		act_gen_df['ActualGenerationOutput'] = round(act_gen_df.resample('H').mean()['ActualGenerationOutput'], 2)
		# now drop the unnecessary rows
		act_gen_df.dropna(subset=["ActualGenerationOutput"], inplace=True)
		# now set 'DateTime' back as column
		act_gen_df.reset_index(inplace=True)

		"""check if start and end of month is in data"""
		# find out if first day is in list- first fill days, then hours
		firsttimestamp = (act_gen_df['DateTime']).iloc[0]
		# check if 'firsttimestamp' is not first of the month
		if firsttimestamp.day != 1 or firsttimestamp.hour != 0:
			# if so create a datetime obj of the first day of month
			dayone = firsttimestamp.replace(day=1, hour=0)
			# now add to the sorted DF sorted_df, add in -1 pos and then add one to overall-index
			act_gen_df.loc[-1] = (dayone, areatypecode, country, technology, np.nan)
			act_gen_df.index = act_gen_df.index+1
			act_gen_df.sort_values(by='DateTime', inplace=True)
		# just to check if if-clause is working
		#else:
		#	print("first of the month is in list")

		# now we check for the last of the month
		lastindex = len(act_gen_df.index)-1
		last_timestamp = act_gen_df['DateTime'].iloc[lastindex]
		#  calendar.monthrange return a tuple
		#  (weekday of first day of the month, number of days in month)
		last_day_of_month = calendar.monthrange(last_timestamp.year, last_timestamp.month)[1]
		# checks if date is not last day of month or not last hour
		if last_timestamp.date() != date(last_timestamp.year, last_timestamp.month, last_day_of_month) or \
				last_timestamp.hour != int('23'):
			# if so we create a datetime with the last day and add it to the dataframe
			last_day_as_date = dt(last_timestamp.year, last_timestamp.month, last_day_of_month, 23)
			act_gen_df.loc[-1] = (last_day_as_date, areatypecode, country, technology, np.nan)
			act_gen_df.index = act_gen_df.index+1
			act_gen_df.sort_values(by='DateTime', inplace=True)
		# just to check if if-clause is working
		#else:
		#	print("last of the month is in list")

		# print the auxiliary-dataframe into a csv
		act_gen_df.to_csv('data/'+str(year)+'/'+country+'/raw_sorted_tech/'+str(month)+'_'+areatypecode+'_'+technology+'.csv',
		                  sep='\t', encoding='utf-8', index=False,
		                  header=['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput'])

		"""iterate to find the gaps"""
		# compare the date then time
		# init old datetime as first datetime of dataframe and create gap-list
		old_date = firsttimestamp
		gap_list = []
		# loop over every datetime-obj check if gap by comparing new and old
		for datetime in act_gen_df['DateTime']:
			# set new_date to current datetime
			new_date = datetime
			# compare the time of the dates
			gap_list = gap_list_creator(old_date, new_date, gap_list, areatypecode, country, technology)
			# set the current datetime as old
			old_date = datetime

		"""create a csv with all gaps included"""
		# convert list with the gaps to a dataframe
		gap_df = pd.DataFrame(gap_list)
		# check if the gap-df is empty
		if gap_df.empty:
			#print("there are no gaps")
			gap_df.to_csv('data/'+str(year)+'/'+country+'/gaplists_per_tech/'+str(month)+'_'+areatypecode+'_'
			              + technology+'_empty.csv', sep='\t', encoding='utf-8', index=False)
			# sort everything on the DateTime-column and save as csv
			act_gen_df.sort_values(by='DateTime', inplace=True)
			act_gen_df.reset_index(drop=True, inplace=True)
			# save the final df as csv
			act_gen_df.to_csv('data/'+str(year)+'/'+country+'/final_sorted_tech/'+str(month)+'_'+areatypecode+'_'
			                  + technology+'_nogaps.csv', sep='\t', encoding='utf-8', index=False,
			                  header=['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput'])
		else:
			gap_df.to_csv('data/'+str(year)+'/'+country+'/gaplists_per_tech/'+str(month)+'_'+areatypecode+'_'
			              + technology+'.csv', sep='\t', encoding='utf-8', index=False,
			              header=['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput'])
			# concat both csv to have a list with filled in gaps then save as csv
			sorted_tech_csv = pd.read_csv('data/'+str(year)+'/'+country+'/raw_sorted_tech/'+str(month)+'_'
			                              + areatypecode+'_'+technology+'.csv', sep='\t', encoding='utf-8')
			gap_list_csv = pd.read_csv('data/'+str(year)+'/'+country+'/gaplists_per_tech/'+str(month)+'_'
			                           + areatypecode+'_'+technology+'.csv', sep='\t', encoding='utf-8')
			dataframes = [sorted_tech_csv, gap_list_csv]
			final_df = pd.concat(dataframes)
			# sort everything on the DateTime-column and save as csv
			final_df.sort_values(by='DateTime', inplace=True)
			final_df.reset_index(drop=True, inplace=True)
			# save the final df as csv
			final_df.to_csv('data/'+str(year)+'/'+country+'/final_sorted_tech/'+str(month)+'_'+areatypecode+'_'
			                + technology+'_wgaps.csv', sep='\t', encoding='utf-8', index=False,
			                header=['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput'])

			# calc missing data in percent and put into list to have an overview
			missing_percent_o = round(calc_missing_data(final_df), 2)
			gap_dict = {'Month': month, 'Country': country, 'Technology': technology, 'AreaTypeCode': areatypecode,
			            'MissingPercentage': missing_percent_o}

			# save the country in the csv of countries with gaps
			with open("countries_w_gaps.csv", "a") as csvfile:
				# create a dict_writer object with the needed attributes
				dictwriter_object = DictWriter(csvfile, delimiter='\t', fieldnames=field_names)
				# write the dict into the csv
				dictwriter_object.writerow(gap_dict)

	except Exception as e:
		#print("Error is found: "+str(e)+"||"+country+"--"+str(month)+"--"+areatypecode+"--"+technology)
		pass


def gap_list_creator(old_date, new_date, gap_list, areatypecode, country, technology):
	"""
	find gaps between the start and end datetime and return the whole list of gaps

	:param old_date: the date from which we start to check for gaps
	:param new_date: the final date
	:param gap_list: list with already found gaps

	The following inputs are just for proper saving
	:param areatypecode: MBA, BZN, CTA or CTY
	:param country: code for the country
	:param technology: tehnology used

	:return: updated list of gaps found in data
	"""
	# add an hour to check for gap
	old_h_added = old_date+pd.Timedelta(1, unit='H')

	# if old_h_added is same or bigger than new_date we have no gap
	if old_h_added >= new_date:
		return gap_list
	else:
		# add every missing datetime between start(old_date) and end(new_date); start exclusive
		for timestamp in pd.date_range(old_date, new_date, freq='H', closed='right'):
			# because end is inclusive we have to check if we reached the end
			if timestamp != new_date:
				# create a datetime obj from the timestamp
				datetime_obj = timestamp.to_pydatetime()
				# saves the gap with null-value
				gap_list.append((datetime_obj, areatypecode, country, technology, np.nan))
		return gap_list
