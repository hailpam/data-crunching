import sys
import os
sys.path.append(os.path.abspath(__file__).replace('tests/test_util.py', ''))

import unittest

from scripts.util import *

class TestUtil(unittest.TestCase):
    def test_name_to_camelcase(self):
        name = 'AUDES GROUP'
        self.assertEqual(name_to_camelcase(name), 'Audes Group')

        name = 'Via Noventana, 192'
        self.assertEqual(name_to_camelcase(name), 'Via Noventana, 192')

        name = 'NOVENTANA'
        self.assertEqual(name_to_camelcase(name), 'Noventana')

        name = "Via Dell'industria"
        self.assertEqual(name_to_camelcase(name), "Via Dell'Industria")

        name = "Via Dell'arrigo'"
        self.assertEqual(name_to_camelcase(name), "Via Dell'Arrigo'")

        name = "RO' dell'artulo'"
        self.assertEqual(name_to_camelcase(name), "Ro' Dell'Artulo'")

        name = "RO' 'dell'artulo'"
        self.assertEqual(name_to_camelcase(name), "Ro' 'Dell'Artulo'")

if __name__ == '__main__':
    unittest.main()
