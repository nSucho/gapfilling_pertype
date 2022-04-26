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
    countries_df = pd.read_csv('country_list.csv', sep='\t', encoding='utf-8')
    areatypecodes_df = pd.read_csv('areatypecode_list.csv', sep='\t', encoding='utf-8')
    technologies_df = pd.read_csv('technology_list.csv', sep='\t', encoding='utf-8')

    for atcode in areatypecodes_df:
        for technology in technologies_df:
            for country in countries_df:
                # unify the year to fill the gaps afterwards
                gap_filling_aux.unify_year(year, country, atcode, technology)


if __name__ == '__main__':
    gapfill_main()

