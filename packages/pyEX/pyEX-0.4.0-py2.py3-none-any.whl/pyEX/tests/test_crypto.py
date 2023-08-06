# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#

import atexit
import pickle

# for Coverage
import time

from mock import MagicMock, patch

atexit.register = MagicMock()
pickle.dump = MagicMock()


SYMBOL = "BTCUSD"


class TestAll:
    def teardown(self):
        time.sleep(0.1)  # prevent being blocked

    def test_bookcrypto(self):
        from pyEX import Client

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            mock.return_value.json = MagicMock(return_value=[])

            c = Client(version="sandbox")
            c.cryptoBookDF(SYMBOL)

    def test_pricecrypto(self):
        from pyEX import Client

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            mock.return_value.json = MagicMock(return_value=[])

            c = Client(version="sandbox")
            c.cryptoPriceDF(SYMBOL)

    def test_quotecrypto(self):
        from pyEX import Client

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            mock.return_value.json = MagicMock(return_value=[])

            c = Client(version="sandbox")
            c.cryptoQuoteDF(SYMBOL)
