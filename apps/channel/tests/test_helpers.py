import unittest

from apps.channel.helpers import *

class TestHelpers(unittest.TestCase):

    def test_source_from_exchange(self):
        self.assertEqual(source_code_from_name('poloniex'), 0)
        self.assertEqual(source_code_from_name('BinancE'), 2)
        self.assertEqual(source_code_from_name('kucoin'), 4)
        self.assertIsNone(source_code_from_name('xxx'))


    def test_source_name_from_code(self):
        self.assertEqual(source_name_from_code(0), 'poloniex')
        self.assertEqual(source_name_from_code(3), 'bitfinex')
        self.assertEqual(source_name_from_code(4), 'kucoin')
        self.assertIsNone(source_name_from_code(99))

    def test_counter_currency_code_from_name(self):
        self.assertEqual(counter_currency_code_from_name('BTC'), 0)
        self.assertEqual(counter_currency_code_from_name('uSdt'), 2)
        self.assertEqual(counter_currency_code_from_name('XMR'), 3)
        self.assertIsNone(counter_currency_code_from_name('XXX'))