"""
Analisi dei campi
"""
import pandas as pd
import numpy as np
from sys import float_info


def fielddata_to_series(field_data):
    return pd.Series(field_data, index=range(0, len(field_data)))


def series_to_filedata(s):
    s = s.dropna()
    s = s.astype(dtype='float32')
    s = s.replace(np.inf, float_info.max)
    s = s.replace(-np.inf, float_info.min)
    return s.values


def fft(data, kargs):
    s = fielddata_to_series(data)
    s = fielddata_to_series(np.fft.fft(s, **kargs))
    s = s.apply(np.log)
    return series_to_filedata(s)


def ewma(data, kargs):
    s = fielddata_to_series(data)
    s = pd.ewma(s, **kargs)
    return series_to_filedata(s)
