# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
import itertools
from functools import wraps

import pandas as pd

from ..common import _expire, _get, _reindex, _strOrDate


def latestFX(symbols=None, token="", version="stable", filter="", format="json"):
    """This endpoint returns real-time foreign currency exchange rates data updated every 250 milliseconds.

    https://iexcloud.io/docs/api/#latest-currency-rates
    5pm Sun-4pm Fri UTC

    Args:
        symbols (str): comma seperated list of symbols
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict: result
    """
    if symbols:
        if isinstance(symbols, str):
            return _get(
                "/fx/latest?symbols={symbols}".format(symbols=symbols),
                token=token,
                version=version,
                filter=filter,
                format=format,
            )
        return _get(
            "/fx/latest?symbols={symbols}".format(symbols=",".join(symbols)),
            token=token,
            version=version,
            filter=filter,
            format=format,
        )
    return _get(
        "/fx/latest", token=token, version=version, filter=filter, format=format
    )


@wraps(latestFX)
def latestFXDF(*args, **kwargs):
    return pd.DataFrame(latestFX(*args, **kwargs))


def convertFX(
    symbols=None,
    amount=None,
    token="",
    version="stable",
    filter="",
    format="json",
):
    """This endpoint performs a conversion from one currency to another for a supplied amount of the base currency. If an amount isn’t provided, the latest exchange rate will be provided and the amount will be null.

    https://iexcloud.io/docs/api/#currency-conversion
    5pm Sun-4pm Fri UTC

    Args:
        symbols (str): comma seperated list of symbols
        amount (float): amount to convert
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict: result
    """
    amount = amount or ""
    if symbols:
        if isinstance(symbols, str):
            return _get(
                "/fx/convert?symbols={symbols}&amount={amount}".format(
                    symbols=symbols, amount=amount
                ),
                token=token,
                version=version,
                filter=filter,
                format=format,
            )
        return _get(
            "/fx/convert?symbols={symbols}&amount={amount}".format(
                symbols=",".join(symbols), amount=amount
            ),
            token=token,
            version=version,
            filter=filter,
            format=format,
        )
    return _get(
        "/fx/convert?amount={amount}".format(amount=amount),
        token=token,
        version=version,
        filter=filter,
        format=format,
    )


@wraps(convertFX)
def convertFXDF(*args, **kwargs):
    return pd.DataFrame(convertFX(*args, **kwargs))


@_expire(hour=1)
def historicalFX(
    symbols=None,
    from_="",
    to_="",
    on="",
    last=0,
    first=0,
    token="",
    version="stable",
    filter="",
    format="json",
):
    """This endpoint returns a daily value for the desired currency pair.

    https://iexcloud.io/docs/api/#historical-daily
    1am Mon-Sat UTC

    Args:
        symbols (str): comma seperated list of symbols
        from_ (str or datetime): Returns data on or after the given from date. Format YYYY-MM-DD
        to_ (str or datetime): Returns data on or before the given to date. Format YYYY-MM-DD
        on (str or datetime): Returns data on the given date. Format YYYY-MM-DD
        last (int): Returns the latest n number of records in the series
        first (int): Returns the first n number of records in the series
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict: result
    """
    base_url = "/fx/historical?"

    if symbols:
        if isinstance(symbols, str):
            base_url += "symbols={symbols}&".format(symbols=symbols)
        else:
            base_url += "symbols={symbols}&".format(symbols=",".join(symbols))

    if from_:
        base_url += "from={}&".format(_strOrDate(from_))
    if to_:
        base_url += "to={}&".format(_strOrDate(to_))
    if on:
        base_url += "on={}&".format(_strOrDate(on))
    if last:
        base_url += "last={}&".format(str(last))
    if first:
        base_url += "first={}&".format(str(first))

    return list(
        itertools.chain.from_iterable(
            _get(base_url, token=token, version=version, filter=filter, format=format)
        )
    )


@wraps(historicalFX)
def historicalFXDF(*args, **kwargs):
    df = _reindex(pd.DataFrame(historicalFX(*args, **kwargs)), ["date", "symbol"])
    df.sort_index(inplace=True)
    return df
