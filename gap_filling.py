"""
Created on April 2022

@author: Niko Suchowitz
"""
import filling_fedot


def gapfill_main():
    """

    :return:
    """

    # filling the gaps with fedot
    filling_fedot.readin_fedot(year='2021', areatypecode='BZN', country='IE_SEM', technology='Fossil Peat')
    # filling the gaps with Kalman-filter


if __name__ == '__main__':
    gapfill_main()

