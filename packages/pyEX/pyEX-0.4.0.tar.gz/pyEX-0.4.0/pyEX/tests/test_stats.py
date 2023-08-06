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
from mock import MagicMock, patch

atexit.register = MagicMock()
pickle.dump = MagicMock()


class TestAll:
    def test_stats(self):
        from pyEX.stats import stats

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            stats()

    def test_statsDF(self):
        from pyEX.stats import statsDF

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            mock.return_value.json = MagicMock(return_value=[])
            statsDF()

    def test_recent(self):
        from pyEX.stats import recent

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            recent()

    def test_recentDF(self):
        from pyEX.stats import recentDF

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            mock.return_value.json = MagicMock(return_value=[])
            recentDF()

    def test_records(self):
        from pyEX.stats import records

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            records()

    def test_recordsDF(self):
        from pyEX.stats import recordsDF

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            mock.return_value.json = MagicMock(return_value=[])
            recordsDF()

    def test_summary(self):
        from datetime import datetime

        from pyEX.common import PyEXception
        from pyEX.stats import summary

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            summary()
            summary("201505")
            summary(datetime.today())
            try:
                summary(5)
                assert False
            except PyEXception:
                pass

    def test_summaryDF(self):
        from datetime import datetime

        from pyEX.stats import summaryDF

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            mock.return_value.json = MagicMock(return_value=[])
            summaryDF()
            summaryDF("201505")
            summaryDF(datetime.today())

    def test_daily(self):
        from datetime import datetime

        from pyEX.common import PyEXception
        from pyEX.stats import daily

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            daily()
            daily("201505")
            daily(last="5")
            daily(datetime.today())
            try:
                daily(5)
                assert False
            except PyEXception:
                pass

    def test_dailyDF(self):
        from datetime import datetime

        from pyEX.stats import dailyDF

        with patch("requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.status_code = 200
            mock.return_value.json = MagicMock(return_value=[])
            dailyDF()
            dailyDF("201505")
            dailyDF(last="5")
            dailyDF(datetime.today())
