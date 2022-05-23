"""
Created on May 2022

@author: Niko Suchowitz
"""


def kalman_method(data_w_nan, country, year, atc, tech):
    """
    The kalman-filter

    :param data_w_nan: the data with gaps (NaN) to fill
    :param country:
	:param year:
	:param atc:
	:param tech:
	:return: the data with filled gaps (NaN)
	"""

    # TODO: 2x2 möglichkeiten (smooth, nicht smooth, arima, structts)
