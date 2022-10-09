"""
Created on April 2022

@author: Niko Suchowitz
"""
from datetime import datetime as dt
from datetime import date
import calendar
from readin_SFTP import readin_aux
import pandas as pd
import numpy as np
import warnings

pd.options.mode.chained_assignment = None  # default='warn'
warnings.simplefilter(action='ignore', category=FutureWarning)


def check_for_gaps(file_df_original, areatypecode, country, technology, month, year, val_col, header,
                   datatype):
    """
    checks the original dataframe for gaps
    :param file_df_original: the original dataframe
    :type file_df_original: dataframe
    :param areatypecode: area type code of the original dataframe
    :type areatypecode: string
    :param country: country code of the original dataframe
    :type country: string
    :param technology: technology of the original dataframe
    :type technology: string
    :param month: month of the data
    :type month: int
    :param year: year of the data
    :type year: string
    :param val_col: header of the column with the important values
    :type val_col: string
    :param header: whole header of the dataframe
    :type header: list
    :param datatype: type of the data
    :type datatype: string
    :return:
    :rtype:
    """
    file_df = file_df_original.copy()

    # ----------
    # check if necessary folders exist, else create
    # ----------
    path = 'data/' + datatype + '/' + str(year) + '/' + country
    readin_aux.create_path(path + '/rawdata_sorted')
    readin_aux.create_path(path + '/final_sorted')
    readin_aux.create_path(path + '/gaplists')

    # some (country, ATC, Technology)-combinations do not exist, so catch the error for this countries
    try:
        # only take rows into 'act_data_df' which are equal to our wanted attributes
        if datatype == 'agpt':
            act_data_df = file_df.loc[(file_df["MapCode"] == country) & (file_df["ProductionType"] == technology) &
                                      (file_df["AreaTypeCode"] == areatypecode)]
            if technology == 'Fossil Brown coal/Lignite':
                technology = 'Fossil Brown coal Lignite'
        elif datatype == 'totalload':
            act_data_df = file_df.loc[(file_df["MapCode"] == country) & (file_df["AreaTypeCode"] == areatypecode)]

        # ----------
        # if the 'DateTime' is not in hourly steps, we down sample to hours
        # ----------
        # first we have to set the 'DateTime' as index
        act_data_df = act_data_df.set_index(['DateTime'])
        # now resample
        act_data_df[val_col] = round(act_data_df.resample('H').mean()[val_col], 2)
        # now drop the unnecessary rows
        act_data_df.dropna(subset=[val_col], inplace=True)
        # now set 'DateTime' back as column
        act_data_df.reset_index(inplace=True)

        # ----------
        # check if start and end of month is in data
        # ----------
        # find out if first day is in list
        # first fill days, then hours
        firsttimestamp = (act_data_df['DateTime']).iloc[0]
        # check if 'firsttimestamp' is not first of the month
        if firsttimestamp.day != 1 or firsttimestamp.hour != 0:
            # if so create a datetime obj of the first day of month
            dayone = firsttimestamp.replace(day=1, hour=0)
            # now add to the sorted DF sorted_df, add in -1 pos and then add one to overall-index
            # if datatype == 'agpt' the column 'technology' is added
            if datatype == 'agpt':
                act_data_df.loc[-1] = (dayone, areatypecode, country, technology, np.nan)
            else:
                act_data_df.loc[-1] = (dayone, areatypecode, country, np.nan)
            act_data_df.index = act_data_df.index + 1
            act_data_df.sort_values(by='DateTime', inplace=True)
        # just to check if if-clause is working
        # else:
        # print("first of the month is in list")

        # now we check for the last of the month
        lastindex = len(act_data_df.index) - 1
        last_timestamp = act_data_df['DateTime'].iloc[lastindex]
        #  calendar.monthrange return a tuple
        #  (weekday of first day of the month, number of days in month)
        last_day_of_month = calendar.monthrange(last_timestamp.year, last_timestamp.month)[1]
        # checks if date is not last day of month or not last hour
        if last_timestamp.date() != date(last_timestamp.year, last_timestamp.month, last_day_of_month) or\
           last_timestamp.hour != int('23'):
            # if so we create a datetime with the last day and add it to the dataframe
            last_day_as_date = dt(last_timestamp.year, last_timestamp.month, last_day_of_month, 23)
            # if datatype == 'agpt' the column 'technology' is added
            if datatype == 'agpt':
                act_data_df.loc[-1] = (last_day_as_date, areatypecode, country, technology, np.nan)
            else:
                act_data_df.loc[-1] = (last_day_as_date, areatypecode, country, np.nan)
            act_data_df.index = act_data_df.index + 1
            act_data_df.sort_values(by='DateTime', inplace=True)
        # just to check if if-clause is working
        # else:
        # print("last of the month is in list")

        # save the auxiliary-dataframe into a csv
        act_data_df.to_csv(path + '/rawdata_sorted/' + str(month) +
                           '_' + areatypecode + '_' + technology + '.csv', sep='\t', encoding='utf-8', index=False,
                           header=header)

        # ----------
        # iterate to find the gaps
        # ----------
        # compare the date then time
        # init old datetime as first datetime of dataframe and create gap-list
        old_date = firsttimestamp
        gap_list = []
        # loop over every datetime-obj check if gap by comparing new and old
        for datetime in act_data_df['DateTime']:
            # set new_date to current datetime
            new_date = datetime
            # compare the time of the dates
            gap_list = gap_list_creator(old_date, new_date, gap_list, areatypecode, country, technology)
            # set the current datetime as old
            old_date = datetime

        # ----------
        # create a csv with all gaps included
        # ----------
        # convert list with the gaps to a dataframe
        gap_df = pd.DataFrame(gap_list)
        # check if the gap-df is empty
        if not gap_df.empty:
            # if the datatype is not '' we can drop the technology column
            if not datatype == 'agpt':
                gap_df = gap_df.drop(gap_df.columns[3], axis=1)
            gap_df.to_csv(path + '/gaplists/' + str(month) + '_' +
                          areatypecode + '_' + technology + '.csv', sep='\t', encoding='utf-8', index=False,
                          header=header)
            # concat both csv to have a list with filled in gaps then save as csv
            sorted_tech_csv = pd.read_csv(path + '/rawdata_sorted/' +
                                          str(month) + '_' + areatypecode + '_' + technology + '.csv', sep='\t',
                                          encoding='utf-8')
            gap_list_csv = pd.read_csv(path + '/gaplists/' +
                                       str(month) + '_' + areatypecode + '_' + technology + '.csv', sep='\t',
                                       encoding='utf-8')
            dataframes = [sorted_tech_csv, gap_list_csv]
            final_df = pd.concat(dataframes)
            # sort everything on the DateTime-column and save as csv
            final_df.sort_values(by='DateTime', inplace=True)
            final_df.reset_index(drop=True, inplace=True)
            # save the final df as csv
            final_df.to_csv(path + '/final_sorted/' + str(month) +
                            '_' + areatypecode + '_' + technology + '_wgaps.csv', sep='\t', encoding='utf-8',
                            index=False, header=header)
        else:
            # print("there are no gaps")
            # sort everything on the DateTime-column and save as csv
            act_data_df.sort_values(by='DateTime', inplace=True)
            act_data_df.reset_index(drop=True, inplace=True)
            # save the final df as csv
            act_data_df.to_csv(path + '/final_sorted/' + str(month) +
                               '_' + areatypecode + '_' + technology + '_nogaps.csv', sep='\t', encoding='utf-8',
                               index=False, header=header)
    except Exception as e:
        #print("Error is found: "+str(e)+"||"+country+"--"+str(month)+"--"+areatypecode+"--"+technology)
        pass


def gap_list_creator(old_date, new_date, gap_list, areatypecode, country, technology):
    """
    creates a list of all found gaps in the dataframe
    :param old_date: start date for checking
    :type old_date: date
    :param new_date: finish date for checking
    :type new_date: date
    :param gap_list: list of all gaps found until this point
    :type gap_list: list
    :param areatypecode: area type code of the data
    :type areatypecode: string
    :param country: country code of the data
    :type country: string
    :param technology: technology of the data
    :type technology: string
    :return: list of gaps
    :rtype: list
    """
    # add an hour to check for gap
    old_h_added = old_date + pd.Timedelta(1, unit='H')

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
