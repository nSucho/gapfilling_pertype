"""
Created on April 2022

@author: Niko Suchowitz
"""
import pandas as pd


def analyze_gap_length(check_df, year, month, country, areatypecode, technology):
	"""

	:param check_df:
	:param year:
	:param month:
	:param country:
	:param areatypecode:
	:param technology:
	:return:
	"""

	# works but only hands me the length
	"""# TODO: funktioniert, verschiebt aber zeilen um summe der vorgänger nans, darum gibt erstmal nur länge zurück
	consecutive_gaps = check_df['ActualGenerationOutput'].isnull().astype(int).groupby(
		check_df['ActualGenerationOutput'].notnull().astype(int).cumsum()).sum()
	# drop zero values
	consecutive_gaps = consecutive_gaps.loc[consecutive_gaps != 0]
	consecutive_gaps.to_csv('data/'+str(year)+'/'+country+'/final_sorted_tech/'+str(month)+'_'+areatypecode+'_'
	                        + technology+'_gaps_length.csv', sep='\t', encoding='utf-8', index=False,
	                        header=['Length'])"""

	# works but count doesnt match the proper coloums
	"""check_df['GapLength'] = check_df['ActualGenerationOutput'].isnull().astype(int).groupby(
		check_df['ActualGenerationOutput'].notnull().astype(int).cumsum()).sum()
	# drop zero values
	check_df.to_csv('data/'+str(year)+'/'+country+'/final_sorted_tech/'+str(month)+'_'+areatypecode+'_'
	                        + technology+'_gaps_length.csv', sep='\t', encoding='utf-8', index=False,
	                        header=['DateTime', 'AreaTypeCode', 'MapCode', 'ProductionType', 'ActualGenerationOutput',
	                                'GapLength'])"""

	# gives back length of gaps as index and the amount of the gap-lengths per coloumn
	consecutive_gaps = check_df.apply(lambda d: consecutive_nans(d).value_counts()).fillna(0)
	# drop all coloums except 'ActualGenerationOutput'
	consecutive_gaps = consecutive_gaps[['ActualGenerationOutput']]
	# get the gap-length as own column
	consecutive_gaps.reset_index(inplace=True)
	consecutive_gaps.to_csv('data/'+str(year)+'/'+country+'/'+str(year)+'_'+areatypecode+'_'
	                        + technology+'_gaps_length.csv', sep='\t', encoding='utf-8', index=False,
	                        header=['GapLength', 'AmountInAGO'])


def consecutive_nans(ds):
	"""

	:param ds:
	:return:
	"""
	return ds.isnull().astype(int).groupby(ds.notnull().astype(int).cumsum()).sum()


if __name__ == '__main__':
	# for testing reasons
	year = 2021
	month = 1
	country = 'IE_SEM'
	areatypecode = 'BZN'
	technology = 'Fossil Gas'

	check_df = pd.read_csv('data/'+str(year)+'/'+str(month)+'/'+country+'/final_sorted_tech/'+areatypecode+'/'
	                       + technology+'_'+str(month)+'.csv', sep='\t', encoding='utf-8')

	analyze_gap_length(check_df, year, month, country, areatypecode, technology)