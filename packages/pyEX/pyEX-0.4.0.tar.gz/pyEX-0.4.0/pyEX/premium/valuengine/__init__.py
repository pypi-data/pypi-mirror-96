# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
from ...common import _EST, PyEXception, _expire, _get, _strOrDate


@_expire(hour=10, tz=_EST)
def valuEngineStockResearchReport(symbol="", date=None, token="", version="stable"):
    """ValuEngine provides research on over 5,000 stocks with stock valuations, Buy/Hold/Sell recommendations, and forecasted target prices, so that you the individual investor can make informed decisions. Every ValuEngine Valuation and Forecast model for the U.S. equities markets has been extensively back-tested. ValuEngine’s performance exceeds that of many well-known stock-picking styles. Reports available since March 19th, 2020.
    https://iexcloud.io/docs/api/#valuengine-stock-research-report

    Args:
        symbol (str): symbol to use
    """
    if not symbol or not date:
        raise PyEXception("symbol and date required")
    return _get(
        "files/download/VALUENGINE_REPORT?symbol={}&date={}".format(
            symbol, _strOrDate(date)
        ),
        token=token,
        version=version,
    )
