"""
Created on April 2022

@author: Niko Suchowitz
"""

import gap_filling_aux

def gapfill_main():
    """

    :return:
    """
    year = '2021'
    country = ''
    atc = ''
    technology = ''

    # unify the year to fill the gaps afterwards
    gap_filling_aux.unify_year(year, country, atc, technology)


if __name__ == '__main__':
    gapfill_main()

