# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
from functools import wraps

from ...common import (
    PyEXception,
    _get,
    _raiseIfNotStr,
    _strOrDate,
    _toDatetime,
    json_normalize,
)


def socialSentiment(
    symbol, type="daily", date="", token="", version="stable", filter="", format="json"
):
    """This endpoint provides social sentiment data from StockTwits. Data can be viewed as a daily value, or by minute for a given date.

    https://iexcloud.io/docs/api/#social-sentiment

    Args:
        symbol (str): Symbol to look up
        type (Optional[str]): Can only be daily or minute. Default is daily.
        date (Optional[str]): Format YYYYMMDD date to fetch sentiment data. Default is today.
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)

    if type not in ("daily", "minute"):
        raise PyEXception("`type` must be in (daily, minute). Got: {}".format(type))
    base_url = "stock/{}/sentiment/{}".format(symbol, type)

    if date:
        date = _strOrDate(date)
        base_url += "/{}".format(date)
    return _get(base_url, token, version, filter)


@wraps(socialSentiment)
def socialSentimentDF(*args, **kwargs):
    df = json_normalize(socialSentiment(*args, **kwargs))
    _toDatetime(df)
    return df
