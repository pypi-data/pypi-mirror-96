# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#


def tolist(val):
    try:
        iter(val)
        return val
    except TypeError:
        return [val]
