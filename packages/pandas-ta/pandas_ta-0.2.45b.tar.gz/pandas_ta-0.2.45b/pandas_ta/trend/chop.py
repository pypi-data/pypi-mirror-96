# -*- coding: utf-8 -*-
from numpy import log10 as npLog10
from pandas import DataFrame
from pandas_ta.volatility import atr
from pandas_ta.utils import get_offset, get_drift, verify_series


def chop(high, low, close, length=None, atr_length=None, scalar=None, drift=None, offset=None, **kwargs):
    """Indicator: Choppiness Index (CHOP)"""
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    length = int(length) if length and length > 0 else 14
    atr_length = int(
        atr_length) if atr_length is not None and atr_length > 0 else 1
    scalar = float(scalar) if scalar else 100
    drift = get_drift(drift)
    offset = get_offset(offset)

    # Calculate Result
    diff = high.rolling(length).max() - low.rolling(length).min()

    atr_ = atr(high=high, low=low, close=close, length=atr_length)
    atr_sum = atr_.rolling(length).sum()

    chop = scalar * (npLog10(atr_sum) - npLog10(diff))
    chop /= npLog10(length)

    # Offset
    if offset != 0:
        chop = chop.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        chop.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        chop.fillna(method=kwargs["fill_method"], inplace=True)

    # Name and Categorize it
    chop.name = f"CHOP_{length}_{atr_length}_{scalar}"
    chop.category = "trend"

    return chop


chop.__doc__ = \
"""Choppiness Index (CHOP)

The Choppiness Index was created by Australian commodity trader
E.W. Dreiss and is designed to determine if the market is choppy
(trading sideways) or not choppy (trading within a trend in either
direction). Values closer to 100 implies the underlying is choppier
whereas values closer to 0 implies the underlying is trending.

Sources:
    https://www.tradingview.com/scripts/choppinessindex/
    https://www.motivewave.com/studies/choppiness_index.htm

Calculation:
    Default Inputs:
        length=14, scalar=100, drift=1
    HH = high.rolling(length).max()
    LL = low.rolling(length).min()

    ATR_SUM = SUM(ATR(drift), length)
    CHOP = scalar * (LOG10(ATR_SUM) - LOG10(HH - LL))
    CHOP /= LOG10(length)

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    length (int): It's period. Default: 14
    atr_length (int): Length for ATR. Default: 1
    scalar (float): How much to magnify. Default: 100
    drift (int): The difference period. Default: 1
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""
