import time
import unittest

from tjur.log.logger import Logger
from tjur.exchanges.binance import Binance

logger = Logger()
binance = Binance('', '', logger)


class BinanceTest(unittest.TestCase):

    def test_connection(self):
        conn = binance.check_connection()
        self.assertEqual(str(conn['serverTime'])[:-4], str(
            int(time.time()))[:-1])

    def test_recent_trades(self):
        trades = binance.get_recent_trades('LINKETH', 100)
        self.assertTrue(len(trades) == 100)

    def test_get_current_average_price(self):
        price = binance.get_cur_avg_price('LINKETH')
        self.assertGreater(price, 0)


if __name__ == '__main__':
    unittest.main()
