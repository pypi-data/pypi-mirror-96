# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
from functools import wraps

from ...common import _UTC, _expire
from ...stocks import timeSeries, timeSeriesDF


@_expire(hour=8, tz=_UTC)
def _base(id, symbol="", **kwargs):
    """internal"""
    kwargs["id"] = id
    kwargs["key"] = symbol or kwargs.pop("key", "")
    return timeSeries(**kwargs)


@_expire(hour=8, tz=_UTC)
def _baseDF(id, symbol="", **kwargs):
    """internal"""
    kwargs["id"] = id
    kwargs["key"] = symbol or kwargs.pop("key", "")
    return timeSeriesDF(**kwargs)


@wraps(timeSeries)
def precisionAlphaPriceDynamics(symbol="", **kwargs):
    """Precision Alpha performs an unbiased non-equilibrium market analysis on six months of closing price data for all NASDAQ and NYSE listed equities, every day after market close. Precision Alpha calculates scientifically and exactly: market emotion, power, resistance, noise/efficiency, and next day probabilities
    https://iexcloud.io/docs/api/#precision-alpha-price-dynamics

    Args:
        symbol (str): symbol to use
    """
    return _base(id="PREMIUM_PRECISION_ALPHA_PRICE_DYNAMICS", symbol=symbol, **kwargs)


@wraps(timeSeries)
def precisionAlphaPriceDynamicsDF(symbol="", **kwargs):
    """Precision Alpha performs an unbiased non-equilibrium market analysis on six months of closing price data for all NASDAQ and NYSE listed equities, every day after market close. Precision Alpha calculates scientifically and exactly: market emotion, power, resistance, noise/efficiency, and next day probabilities
    https://iexcloud.io/docs/api/#precision-alpha-price-dynamics

    Args:
        symbol (str): symbol to use
    """
    return _baseDF(id="PREMIUM_PRECISION_ALPHA_PRICE_DYNAMICS", symbol=symbol, **kwargs)
