# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
import itertools
from multiprocessing.pool import ThreadPool

import pandas as pd

from ..common import (
    _BATCH_TYPES,
    _TIMEFRAME_CHART,
    PyEXception,
    _get,
    _quoteSymbols,
    _raiseIfNotStr,
    _strOrDate,
    _toDatetime,
    json_normalize,
)
from .fundamentals import _dividendsToDF, _earningsToDF, _financialsToDF, _splitsToDF
from .news import _newsToDF
from .prices import _bookToDF, _chartToDF, chart
from .profiles import _companyToDF, _peersToDF
from .research import _statsToDF

_MAPPING = {
    "book": _bookToDF,
    "chart": _chartToDF,
    "company": _companyToDF,
    "dividends": _dividendsToDF,
    "earnings": _earningsToDF,
    "financials": _financialsToDF,
    "stats": _statsToDF,
    "news": _newsToDF,
    "peers": _peersToDF,
    "splits": _splitsToDF,
}


def batch(
    symbols,
    fields=None,
    range_="1m",
    last=10,
    token="",
    version="stable",
    filter="",
    format="json",
):
    """Batch several data requests into one invocation. If no `fields` passed in, will default to `quote`

    https://iexcloud.io/docs/api/#batch-requests


    Args:
        symbols (str or list): List of tickers to request
        fields (str or list): List of fields to request
        range_ (str): Date range for chart
        last (int):
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict: results in json
    """
    fields = fields or "quote"

    if not isinstance(symbols, [].__class__) and not isinstance(symbols, str):
        raise PyEXception(
            "batch expects string or list of strings for symbols argument"
        )

    if isinstance(fields, str) and "," not in fields:
        fields = [fields]
    elif isinstance(fields, str):
        fields = fields.split(",")

    for field in fields:
        if field not in _BATCH_TYPES:
            raise PyEXception("Unrecognized batch request field: {}".format(field))

    if range_ not in _TIMEFRAME_CHART:
        raise PyEXception("Range must be in %s" % str(_TIMEFRAME_CHART))

    symbols = _quoteSymbols(symbols)
    if len(symbols.split(",")) > 100:
        raise PyEXception("IEX will only handle up to 100 symbols at a time!")

    if "," not in symbols:
        route = "stock/{}/batch?types={}&range={}&last={}".format(
            symbols, ",".join(fields), range_, last
        )
    else:
        route = "stock/market/batch?symbols={}&types={}&range={}&last={}".format(
            symbols, ",".join(fields), range_, last
        )

    return _get(route, token=token, version=version, filter=filter, format=format)


def batchDF(
    symbols,
    fields=None,
    range_="1m",
    last=10,
    token="",
    version="stable",
    filter="",
    format="json",
):
    """Batch several data requests into one invocation

    https://iexcloud.io/docs/api/#batch-requests


    Args:
        symbols (list): List of tickers to request
        fields (list): List of fields to request
        range_ (str): Date range for chart
        last (int):
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        DataFrame: results in json
    """
    symbols = _quoteSymbols(symbols)
    x = batch(
        symbols,
        fields,
        range_,
        last,
        token=token,
        version=version,
        filter=filter,
        format=format,
    )

    ret = {}

    if "," not in symbols:
        # one level json, break down
        for field in x.keys():
            ret[field] = _MAPPING.get(field, json_normalize)(x[field])
    else:
        # two level json
        for symbol in x.keys():
            for field in x[symbol].keys():
                if field not in ret:
                    ret[field] = pd.DataFrame()

                dat = x[symbol][field]
                dat = _MAPPING.get(field, json_normalize)(dat)
                dat["symbol"] = symbol

                ret[field] = pd.concat([ret[field], dat], sort=True)
    return ret


def bulkBatch(
    symbols,
    fields=None,
    range_="1m",
    last=10,
    token="",
    version="stable",
    filter="",
    format="json",
):
    """Optimized batch to fetch as much as possible at once

    https://iexcloud.io/docs/api/#batch-requests


    Args:
        symbols (list): List of tickers to request
        fields (list): List of fields to request
        range_ (str): Date range for chart
        last (int):
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict: results in json
    """
    fields = fields or _BATCH_TYPES
    args = []
    empty_data = []
    list_orig = empty_data.__class__

    if not isinstance(symbols, list_orig):
        raise PyEXception("Symbols must be of type list")

    for i in range(0, len(symbols), 99):
        args.append(
            (symbols[i : i + 99], fields, range_, last, token, version, filter, format)
        )

    pool = ThreadPool(20)
    rets = pool.starmap(batch, args)
    pool.close()

    ret = {}

    for i, d in enumerate(rets):
        symbols_subset = args[i][0]
        if len(d) != len(symbols_subset):
            empty_data.extend(list_orig(set(symbols_subset) - set(d.keys())))
        ret.update(d)

    for k in empty_data:
        if k not in ret:
            if isinstance(fields, str):
                ret[k] = {}
            else:
                ret[k] = {x: {} for x in fields}
    return ret


def bulkBatchDF(
    symbols,
    fields=None,
    range_="1m",
    last=10,
    token="",
    version="stable",
    filter="",
    format="json",
):
    """Optimized batch to fetch as much as possible at once

    https://iexcloud.io/docs/api/#batch-requests


    Args:
        symbols (list): List of tickers to request
        fields (list): List of fields to request
        range_ (str): Date range for chart
        last (int):
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        DataFrame: results in json
    """
    dat = bulkBatch(
        symbols,
        fields,
        range_,
        last,
        token=token,
        version=version,
        filter=filter,
        format=format,
    )
    ret = {}
    for symbol in dat:
        for field in dat[symbol]:
            if field not in ret:
                ret[field] = pd.DataFrame()

            d = dat[symbol][field]
            d = _MAPPING[field](d)
            d["symbol"] = symbol
            ret[field] = pd.concat([ret[field], d], sort=True)

    return ret


def bulkMinuteBars(symbol, dates, token="", version="stable", filter="", format="json"):
    """fetch many dates worth of minute-bars for a given symbol"""
    _raiseIfNotStr(symbol)
    dates = [_strOrDate(date) for date in dates]
    list_orig = dates.__class__

    args = []
    for date in dates:
        args.append((symbol, "1d", date, token, version, filter, format))

    pool = ThreadPool(20)
    rets = pool.starmap(chart, args)
    pool.close()

    return list_orig(itertools.chain(*rets))


def bulkMinuteBarsDF(
    symbol, dates, token="", version="stable", filter="", format="json"
):
    """fetch many dates worth of minute-bars for a given symbol"""
    data = bulkMinuteBars(
        symbol, dates, token=token, version=version, filter=filter, format=format
    )
    df = pd.DataFrame(data)
    if df.empty:
        return df
    _toDatetime(df)
    df.set_index(["date", "minute"], inplace=True)
    return df
