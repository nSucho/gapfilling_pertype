"""
Created on April 2022

@author: Niko Suchowitz
"""
import pandas as pd
import gap_filling_aux

def gapfill_main():
    """

    :return:
    """
    year = '2021'
    # read in the countries-list as dataframe and convert to list
    countries_df = pd.read_csv('country_list.csv', sep='\t', encoding='utf-8')
    countries_list = countries_df[countries_df.columns[0]].tolist()
    # read in the areatypecodes-list as dataframe and convert to list
    areatypecodes_df = pd.read_csv('areatypecode_list.csv', sep='\t', encoding='utf-8')
    atc_list = areatypecodes_df[areatypecodes_df.columns[0]].tolist()
    # read in the technologies-list as dataframe and convert to list
    technologies_df = pd.read_csv('technology_list.csv', sep='\t', encoding='utf-8')
    tech_list = technologies_df[technologies_df.columns[0]].tolist()

    # unify for every combination the year
    for atcode in atc_list:
        for technology in tech_list:
            for country in countries_list:
                # unify the year to fill the gaps afterwards
                gap_filling_aux.unify_year(year, country, atcode, technology)
    #TODO:gapfilling


if __name__ == '__main__':
    gapfill_main()

