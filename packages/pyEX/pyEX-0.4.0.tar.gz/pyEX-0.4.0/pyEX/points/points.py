# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
from functools import wraps

import pandas as pd

from ..common import _get, _raiseIfNotStr, _toDatetime


def points(
    symbol="market",
    key="",
    token="",
    version="stable",
    filter="",
    format="json",
):
    """Data points are available per symbol and return individual plain text values.
    Retrieving individual data points is useful for Excel and Google Sheet users, and applications where a single, lightweight value is needed.
    We also provide update times for some endpoints which allow you to call an endpoint only once it has new data.


    https://iexcloud.io/docs/api/#data-points

    Args:
        symbol (str): Ticker or market to query
        key (str): data point to fetch. If empty or none, will return available data points
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)
    if key:
        return _get(
            "data-points/{symbol}/{key}".format(symbol=symbol, key=key),
            token=token,
            version=version,
            filter=filter,
            format=format,
        )
    return _get(
        "data-points/{symbol}".format(symbol=symbol),
        token=token,
        version=version,
        filter=filter,
        format=format,
    )


@wraps(points)
def pointsDF(
    symbol="market",
    key="",
    token="",
    version="stable",
    filter="",
    format="json",
):
    _raiseIfNotStr(symbol)
    if key:
        return pd.DataFrame(
            [
                {
                    "symbol": symbol,
                    "key": key,
                    "value": points(symbol, key, token, version, filter, format),
                }
            ]
        )
    return _toDatetime(pd.DataFrame(points(symbol, key, token, version, filter)))
