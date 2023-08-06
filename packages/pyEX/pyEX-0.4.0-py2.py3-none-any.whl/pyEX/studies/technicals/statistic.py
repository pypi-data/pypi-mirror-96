# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
import pandas as pd
import talib as t


def beta(client, symbol, timeframe="6m", highcol="high", lowcol="low", period=14):
    """This will return a dataframe of beta for the given symbol across
    the given timeframe

    Args:
        client (pyEX.Client): Client
        symbol (string): Ticker
        timeframe (string): timeframe to use, for pyEX.chart
        highcol (string): column to use to calculate
        lowcol (string): column to use to calculate
        period (int): period to calculate adx across

    Returns:
        DataFrame: result
    """
    df = client.chartDF(symbol, timeframe)
    beta = t.BETA(
        df[highcol].values.astype(float), df[lowcol].values.astype(float), period
    )
    return pd.DataFrame(
        {highcol: df[highcol].values, lowcol: df[lowcol].values, "beta": beta}
    )


def correl(client, symbol, timeframe="6m", highcol="high", lowcol="low", period=14):
    """This will return a dataframe of Pearson's Correlation Coefficient(r) for the given symbol across
    the given timeframe

    Args:
        client (pyEX.Client): Client
        symbol (string): Ticker
        timeframe (string): timeframe to use, for pyEX.chart
        highcol (string): column to use to calculate
        lowcol (string): column to use to calculate
        period (int): period to calculate adx across

    Returns:
        DataFrame: result
    """
    df = client.chartDF(symbol, timeframe)
    correl = t.CORREL(
        df[highcol].values.astype(float), df[lowcol].values.astype(float), period
    )
    return pd.DataFrame(
        {highcol: df[highcol].values, lowcol: df[lowcol].values, "correl": correl}
    )


def linearreg(client, symbol, timeframe="6m", closecol="close", period=14):
    """This will return a dataframe of linear regression for the given symbol across
    the given timeframe

    Args:
        client (pyEX.Client): Client
        symbol (string): Ticker
        timeframe (string): timeframe to use, for pyEX.chart
        closecol (string): column to use to calculate
        period (int): period to calculate adx across

    Returns:
        DataFrame: result
    """
    df = client.chartDF(symbol, timeframe)
    linearreg = t.LINEARREG(df[closecol].values.astype(float), period)
    return pd.DataFrame({closecol: df[closecol].values, "lineearreg": linearreg})


def linearreg_angle(client, symbol, timeframe="6m", closecol="close", period=14):
    """This will return a dataframe of linear regression angle for the given symbol across
    the given timeframe

    Args:
        client (pyEX.Client): Client
        symbol (string): Ticker
        timeframe (string): timeframe to use, for pyEX.chart
        closecol (string): column to use to calculate
        period (int): period to calculate adx across

    Returns:
        DataFrame: result
    """
    df = client.chartDF(symbol, timeframe)
    linearreg = t.LINEARREG_ANGLE(df[closecol].values.astype(float), period)
    return pd.DataFrame({closecol: df[closecol].values, "lineearreg_angle": linearreg})


def linearreg_intercept(client, symbol, timeframe="6m", closecol="close", period=14):
    """This will return a dataframe of linear regression intercept for the given symbol across
    the given timeframe

    Args:
        client (pyEX.Client): Client
        symbol (string): Ticker
        timeframe (string): timeframe to use, for pyEX.chart
        closecol (string): column to use to calculate
        period (int): period to calculate adx across

    Returns:
        DataFrame: result
    """
    df = client.chartDF(symbol, timeframe)
    linearreg = t.LINEARREG_INTERCEPT(df[closecol].values.astype(float), period)
    return pd.DataFrame(
        {closecol: df[closecol].values, "lineearreg_intercept": linearreg}
    )


def linearreg_slope(client, symbol, timeframe="6m", closecol="close", period=14):
    """This will return a dataframe of linear regression slope for the given symbol across
    the given timeframe

    Args:
        client (pyEX.Client): Client
        symbol (string): Ticker
        timeframe (string): timeframe to use, for pyEX.chart
        closecol (string): column to use to calculate
        period (int): period to calculate adx across

    Returns:
        DataFrame: result
    """
    df = client.chartDF(symbol, timeframe)
    linearreg = t.LINEARREG_SLOPE(df[closecol].values.astype(float), period)
    return pd.DataFrame({closecol: df[closecol].values, "lineearreg_slope": linearreg})


def stddev(client, symbol, timeframe="6m", closecol="close", period=14, nbdev=1):
    """This will return a dataframe of standard deviation for the given symbol across
    the given timeframe

    Args:
        client (pyEX.Client): Client
        symbol (string): Ticker
        timeframe (string): timeframe to use, for pyEX.chart
        closecol (string): column to use to calculate
        period (int): period to calculate adx across
        nbdev (int):

    Returns:
        DataFrame: result
    """
    df = client.chartDF(symbol, timeframe)
    stddev = t.STDDEV(df[closecol].values.astype(float), period, nbdev)
    return pd.DataFrame({closecol: df[closecol].values, "stddev": stddev})


def tsf(client, symbol, timeframe="6m", closecol="close", period=14, nbdev=1):
    """This will return a dataframe of standard deviation for the given symbol across
    the given timeframe

    Args:
        client (pyEX.Client): Client
        symbol (string): Ticker
        timeframe (string): timeframe to use, for pyEX.chart
        closecol (string): column to use to calculate
        period (int): period to calculate adx across

    Returns:
        DataFrame: result
    """
    df = client.chartDF(symbol, timeframe)
    tsf = t.TSF(df[closecol].values.astype(float), period)
    return pd.DataFrame({closecol: df[closecol].values, "tsf": tsf})


def var(client, symbol, timeframe="6m", closecol="close", period=14, nbdev=1):
    """This will return a dataframe of var for the given symbol across
    the given timeframe

    Args:
        client (pyEX.Client): Client
        symbol (string): Ticker
        timeframe (string): timeframe to use, for pyEX.chart
        closecol (string): column to use to calculate
        period (int): period to calculate adx across
        nbdev (int):

    Returns:
        DataFrame: result
    """
    df = client.chartDF(symbol, timeframe)
    var = t.VAR(df[closecol].values.astype(float), period, nbdev)
    return pd.DataFrame({closecol: df[closecol].values, "var": var})
