# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
from functools import wraps

import pandas as pd

from ..common import (
    _EST,
    _INDICATOR_RETURNS,
    _INDICATORS,
    _KEY_STATS,
    _TIMEFRAME_CHART,
    _UTC,
    PyEXception,
    _checkPeriodLast,
    _expire,
    _get,
    _quoteSymbols,
    _raiseIfNotStr,
    _reindex,
    _toDatetime,
    json_normalize,
)
from .prices import _chartToDF


@_expire(hour=4, tz=_EST)
def advancedStats(symbol, token="", version="stable", filter="", format="json"):
    """Returns everything in key stats plus additional advanced stats such as EBITDA, ratios, key financial data, and more.

    https://iexcloud.io/docs/api/#advanced-stats
    4am, 5am ET

    Args:
        symbol (str): Ticker to request
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)
    return _get(
        "stock/{symbol}/advanced-stats".format(symbol=_quoteSymbols(symbol)),
        token=token,
        version=version,
        filter=filter,
        format=format,
    )


@wraps(advancedStats)
def advancedStatsDF(*args, **kwargs):
    return _toDatetime(json_normalize(advancedStats(*args, **kwargs)))


@_expire(hour=9, tz=_UTC)
def analystRecommendations(
    symbol, token="", version="stable", filter="", format="json"
):
    """Pulls data from the last four months.

    https://iexcloud.io/docs/api/#analyst-recommendations
    Updates at 9am, 11am, 12pm UTC every day

    Args:
        symbol (str): Ticker to request
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)
    return _get(
        "stock/{symbol}/recommendation-trends".format(symbol=_quoteSymbols(symbol)),
        token=token,
        version=version,
        filter=filter,
        format=format,
    )


@wraps(analystRecommendations)
def analystRecommendationsDF(*args, **kwargs):
    return _toDatetime(json_normalize(analystRecommendations(*args, **kwargs)))


def estimates(
    symbol,
    period="quarter",
    last=1,
    token="",
    version="stable",
    filter="",
    format="json",
):
    """Provides the latest consensus estimate for the next fiscal period

    https://iexcloud.io/docs/api/#estimates
    Updates at 9am, 11am, 12pm UTC every day

    Args:
        symbol (str): Ticker to request
        period (str): Period, either 'annual' or 'quarter'
        last (int): Number of records to fetch, up to 12 for 'quarter' and 4 for 'annual'
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)
    _checkPeriodLast(period, last)
    return _get(
        "stock/{}/estimates?period={}&last={}".format(
            _quoteSymbols(symbol), period, last
        ),
        token=token,
        version=version,
        filter=filter,
        format=format,
    )


def _estimatesToDF(f):
    """internal"""
    if f:
        df = _reindex(
            _toDatetime(json_normalize(f, "estimates", "symbol")), "fiscalEndDate"
        )
    else:
        df = pd.DataFrame()
    return df


@wraps(estimates)
def estimatesDF(*args, **kwargs):
    return _estimatesToDF(estimates(*args, **kwargs))


@_expire(hour=5, tz=_EST)
def fundOwnership(symbol, token="", version="stable", filter="", format="json"):
    """Returns the top 10 fund holders, meaning any firm not defined as buy-side or sell-side such as mutual funds,
       pension funds, endowments, investment firms, and other large entities that manage funds on behalf of others.

    https://iexcloud.io/docs/api/#fund-ownership
    Updates at 5am, 6am ET every day

    Args:
        symbol (str): Ticker to request
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)
    return _get(
        "stock/{symbol}/fund-ownership".format(symbol=_quoteSymbols(symbol)),
        token=token,
        version=version,
        filter=filter,
        format=format,
    )


@wraps(fundOwnership)
def fundOwnershipDF(*args, **kwargs):
    return _toDatetime(pd.DataFrame(fundOwnership(*args, **kwargs)))


@_expire(hour=5, tz=_EST)
def institutionalOwnership(
    symbol, token="", version="stable", filter="", format="json"
):
    """Returns the top 10 institutional holders, defined as buy-side or sell-side firms.

    https://iexcloud.io/docs/api/#institutional-ownership
    Updates at 5am, 6am ET every day

    Args:
        symbol (str): Ticker to request
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)
    return _get(
        "stock/{symbol}/institutional-ownership".format(symbol=_quoteSymbols(symbol)),
        token=token,
        version=version,
        filter=filter,
        format=format,
    )


@wraps(institutionalOwnership)
def institutionalOwnershipDF(*args, **kwargs):
    return _toDatetime(
        pd.DataFrame(institutionalOwnership(*args, **kwargs)),
        cols=[],
        tcols=["reportDate"],
    )


@_expire(hour=8, tz=_EST)
def keyStats(symbol, stat="", token="", version="stable", filter="", format="json"):
    """Key Stats about company

    https://iexcloud.io/docs/api/#key-stats
    8am, 9am ET

    Args:
        symbol (str): Ticker to request
        stat   (Optiona[str]): specific stat to request, in:
                                companyName
                                marketcap
                                week52high
                                week52low
                                week52change
                                sharesOutstanding
                                float
                                avg10Volume
                                avg30Volume
                                day200MovingAvg
                                day50MovingAvg
                                employees
                                ttmEPS
                                ttmDividendRate
                                dividendYield
                                nextDividendDate
                                exDividendDate
                                nextEarningsDate
                                peRatio
                                beta
                                maxChangePercent
                                year5ChangePercent
                                year2ChangePercent
                                year1ChangePercent
                                ytdChangePercent
                                month6ChangePercent
                                month3ChangePercent
                                month1ChangePercent
                                day30ChangePercent
                                day5ChangePercent
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)
    if stat:
        if stat not in _KEY_STATS:
            raise PyEXception("Stat must be in {}".format(_KEY_STATS))
        return _get(
            "stock/{}/stats/{}".format(_quoteSymbols(symbol), stat),
            token=token,
            version=version,
            filter=filter,
            format=format,
        )
    return _get(
        "stock/{}/stats".format(_quoteSymbols(symbol)),
        token=token,
        version=version,
        filter=filter,
        format=format,
    )


def _statsToDF(s):
    """internal"""
    if s:
        df = _reindex(_toDatetime(json_normalize(s)), "symbol")
    else:
        df = pd.DataFrame()
    return df


@wraps(keyStats)
def keyStatsDF(*args, **kwargs):
    return _statsToDF(keyStats(*args, **kwargs))


def priceTarget(symbol, token="", version="stable", filter="", format="json"):
    """Provides the latest avg, high, and low analyst price target for a symbol.

    https://iexcloud.io/docs/api/#price-target
    Updates at 10am, 11am, 12pm UTC every day

    Args:
        symbol (str): Ticker to request
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)
    return _get(
        "stock/{symbol}/price-target".format(symbol=_quoteSymbols(symbol)),
        token=token,
        version=version,
        filter=filter,
        format=format,
    )


@wraps(priceTarget)
def priceTargetDF(*args, **kwargs):
    return _toDatetime(json_normalize(priceTarget(*args, **kwargs)))


@_expire(hour=4, tz=_EST)
def technicals(
    symbol,
    indicator,
    range="1m",
    input1=None,
    input2=None,
    input3=None,
    input4=None,
    token="",
    version="stable",
    filter="",
    format="json",
):
    """Technical indicators are available for any historical or intraday range.

    This endpoint calls the historical or intraday price endpoints for the given range, and the associated indicator for the price range.

    See https://github.com/timkpaine/pyEX-studies for local calculations using TA-lib

    https://iexcloud.io/docs/api/#technical-indicators
    Data Timing: On Demand

    Args:
        symbol (str): Ticker to request
        indicator (str): Technical indicator to request, in:
            Indicator   Description                              Inputs                       Defaults         Outputs
            -------------------------------------------------------------------------------------------------------------
            abs         Vector Absolute Value                                                                   abs
            acos        Vector Arccosine                                                                        acos
            ad          Accumulation/Distribution Line                                                          ad
            add         Vector Addition                                                                          add
            adosc       Accumulation/Distribution Oscillator    short period,long period        2,5             adosc
            adx         Average Directional Movement Index      period                          5               dx
            adxr        Average Directional Movement Rating     period                          5               dx
            ao          Awesome Oscillator                                                                      ao
            apo         Absolute Price Oscillator               short period,long period        2,5             apo
            aroon       Aroon                                   period                          5               aroon_down,aroon_up
            aroonosc    Aroon Oscillator                        period                          5               aroonosc
            asin        Vector Arcsine                                                                          asin
            atan        Vector Arctangent                                                                       atan
            atr         Average True Range                      period                          5               atr
            avgprice    Average Price                                                                           avgprice
            bbands      Bollinger Bands                         period,stddev                   20,2            bbands_lower,bbands_middle,bbands_upper
            bop         Balance of Power
            cci         Commodity Channel Index                 period                          5               cci
            ceil        Vector Ceiling                                                                          ceil
            cmo         Chande Momentum Oscillator              period                          5               cmo
            cos         Vector Cosine                                                                           cos
            cosh        Vector Hyperbolic Cosine                                                                cosh
            crossany    Crossany                                                                                crossany
            crossover   Crossover                                                                               crossover
            cvi         Chaikins Volatility                     period                          5               cvi
            decay       Linear Decay                            period                          5               decay
            dema        Double Exponential Moving Average       period                          5               dema
            di          Directional Indicator                   period                          5               plus_di,minus_di
            div         Vector Division                                                                         div
            dm          Directional Movement                    period                          5               plus_dm,minus_dm
            dpo         Detrended Price Oscillator              period                          5               dpo
            dx          Directional Movement Index              period                          5               dx
            edecay      Exponential Decay                       period                          5               edecay
            ema         Exponential Moving Average              period                          5               ema
            emv         Ease of Movement                                                                        emv
            exp         Vector Exponential                                                                      exp
            fisher      Fisher Transform                        period                          5               fisher,fisher_signal
            floor       Vector Floor                                                                            floor
            fosc        Forecast Oscillator                     period                          5               fosc
            hma         Hull Moving Average                     period                          5               hma
            kama        Kaufman Adaptive Moving Average         period                          5               kama
            kvo         Klinger Volume Oscillator               short period,long period        2,5             kvo
            lag         Lag                                     period                          5               lag
            linreg      Linear Regression                       period                          5               linreg
            linregintercept     Linear Regression Intercept     period                          5               linregintercept
            linregslope         Linear Regression Slope         period                          5               linregslope
            ln          Vector Natural  Log                                                                     ln
            log10       Vector Base-10 Log                                                                      log10
            macd        Moving Average Conv/Div                 short per,long per,signal per   12,26,9         macd,macd_signal,macd_histogram
            marketfi    Market Facilitation Index                                                               marketfi
            mass        Mass Index                              period                          5               mass
            max         Maximum In Period                       period                          5               max
            md          Mean Deviation Over Period              period                          5               md
            medprice    Median Price                                                                            medprice
            mfi         Money Flow Index                        period                          5               mfi
            min         Minimum In Period                       period                          5               min
            mom         Momentum                                period                          5               mom
            msw         Mesa Sine Wave                          period                          5               msw_sine,msw_lead
            mul         Vector Multiplication                                                                   mul
            natr        Normalized Average True Range           period                          5               natr
            nvi         Negative Volume Index                                                                   nvi
            obv         On Balance Volume                                                                       obv
            ppo         Percentage Price Oscillator             short period,long period        2,5             ppo
            psar        Parabolic SAR                           accelfactor step,accel factor max    .2,2       psar
            pvi         Positive Volume Index                                                                   pvi
            qstick      Qstick                                  period                          5               qstick
            roc         Rate of Change                          period                          5               roc
            rocr        Rate of Change Ratio                    period                          5               rocr
            round       Vector Round                                                                            round
            rsi         Relative Strength Index                 period                          5               rsi
            sin         Vector Sine                                                                             sin
            sinh        Vector Hyperbolic Sine                                                                  sinh
            sma         Simple Moving Average                   period                          5               sma
            sqrt        Vector Square Root                                                                      sqrt
            stddev      Standard Deviation Over Period          period                          5               stddev
            stderr      Standard Error Over Period              period                          5               stderr
            stoch       Stochastic Oscillator                   k per,k slowing per,d per       5,3,3           stoch_k,stoch_d
            stochrsi    Stochastic RSI                          period                          5               stochrsi
            sub         Vector Subtraction                                                                      sub
            sum         Sum Over Period                         period                          5               sum
            tan         Vector Tangent                                                                          tan
            tanh        Vector Hyperbolic Tangent                                                               tanh
            tema        Triple Exponential Moving Average       period                          5               tema
            todeg       Vector Degree Conversion                                                                degrees
            torad       Vector Radian Conversion                                                                radians
            tr          True Range                                                                              tr
            trima       Triangular Moving Average               period                          5               trima
            trix        Trix                                    period                          5               trix
            trunc       Vector Truncate                                                                         trunc
            tsf         Time Series Forecast                    period                          5               tsf
            typprice    Typical Price                                                                           typprice
            ultosc      Ultimate Oscillator                     short per,med per,long per      2,3,5           ultosc
            var         Variance Over Period                    period                          5               var
            vhf         Vertical Horizontal Filter              period                          5               vhf
            vidya       Variable Index Dynamic Average          short period,long period,alpha  2,5,.2          vidya
            volatility  Annualized Historical Volatility        period                          5               volatility
            vosc        Volume Oscillator                       short period,long period        2,5             vosc
            vwma        Volume Weighted Moving Average          period                          5               vwma
            wad         Williams Accumulation/Distribution                                                      wad
            wcprice     Weighted Close Price                                                                    wcprice
            wilders     Wilders Smoothing                       period                          5               wilders
            willr       Williams %R    period
            wma         Weighted Moving Average                 period                          5               wma
            zlema       Zero-Lag Exponential Moving Average     period                          5               zlema

        range (str): Timeframe to request e.g. 1m
        input1 (str): input1 to technicals (see docs)
        input2 (str): input2 to technicals (see docs)
        input3 (str): input3 to technicals (see docs)
        input4 (str): input4 to technicals (see docs)
        token (str): Access token
        version (str): API version
        filter (str): filters: https://iexcloud.io/docs/api/#filter-results
        format (str): return format, defaults to json

    Returns:
        dict or DataFrame: result
    """
    _raiseIfNotStr(symbol)
    symbol = _quoteSymbols(symbol)
    if indicator not in _INDICATORS:
        raise PyEXception("indicator must be in {}".format(_INDICATORS))

    if range != "1d":
        if range not in _TIMEFRAME_CHART:
            raise PyEXception("Range must be in {}".format(_TIMEFRAME_CHART))

    base_url = "stock/{}/indicator/{}?range={}".format(symbol, indicator, range)

    # no argument
    if indicator in (
        "abs",
        "acos",
        "ad",
        "add",
        "ao",
        "asin",
        "atan",
        "avgprice",
        "bop",
        "ceil",
        "cos",
        "cosh",
        "crossany",
        "crossover",
        "div",
        "emv",
        "exp",
        "floor",
        "ln",
        "log10",
        "marketfi",
        "medprice",
        "mul",
        "nvi",
        "obv",
        "pvi",
        "round",
        "sin",
        "sinh",
        "sqrt",
        "sub",
        "tan",
        "tanh",
        "todeg",
        "torad",
        "tr",
        "trunc",
        "typprice",
        "wad",
        "wcprice",
        "willr",
    ):
        if input1 or input2 or input3 or input4:
            raise PyEXception("Indicator {} takes no arguments".format(indicator))

    # 1 argument
    if indicator in (
        "aroon",
        "aroonosc",
        "atr",
        "adx",
        "adxr",
        "cci",
        "cmo",
        "cvi",
        "decay",
        "dema",
        "di",
        "dm",
        "dpo",
        "dx",
        "edecay",
        "ema",
        "fisher",
        "fosc",
        "hma",
        "kama",
        "lag",
        "linreg",
        "linregintercept",
        "linregslope",
        "mass",
        "max",
        "md",
        "mfi",
        "min",
        "mom",
        "msw",
        "natr",
        "qstick",
        "roc",
        "rocr",
        "rsi",
        "sma",
        "stddev",
        "stderr",
        "stochrsi",
        "sum",
        "tema",
        "trima",
        "trix",
        "tsf",
        "var",
        "vhf",
        "volatility",
        "vwma",
        "wilders",
        "wma",
        "zlema",
    ):
        if input2 or input3 or input4:
            raise PyEXception("Indicator {} takes at most 1 argument".format(indicator))
        if input1:
            base_url += "&input1={}".format(input1)

    # 2 argument
    if indicator in ("adosc", "apo", "bbands", "kvo", "ppo", "psar", "vosc"):
        if input3 or input4:
            raise PyEXception("Indicator {} takes at most 2 argument".format(indicator))
        if input1:
            base_url += "&input1={}".format(input1)
        if input2:
            base_url += "&input2={}".format(input2)

    # 3 argument
    if indicator in ("macd", "stoch", "ultosc", "vidya"):
        if input4:
            raise PyEXception("Indicator {} takes at most 3 argument".format(indicator))
        if input1:
            base_url += "&input1={}".format(input1)
        if input2:
            base_url += "&input2={}".format(input2)
        if input3:
            base_url += "&input3={}".format(input3)

    return _get(base_url, token=token, version=version, filter=filter, format=format)


@wraps(technicals)
def technicalsDF(
    symbol,
    indicator,
    range="1m",
    input1=None,
    input2=None,
    input3=None,
    input4=None,
    token="",
    version="stable",
    filter="",
    format="json",
):
    json = technicals(
        symbol,
        indicator,
        range,
        input1,
        input2,
        input3,
        input4,
        token=token,
        version=version,
        filter=filter,
        format=format,
    )
    chart = json["chart"]
    seriess = json["indicator"]
    df = _chartToDF(chart)

    for series in seriess:
        for name in _INDICATOR_RETURNS[indicator]:
            df[name] = series
    return df
