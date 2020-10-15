import sys
import os
sys.path.append(os.path.abspath(__file__).replace('tests/test_common.py', ''))

import unittest

class TestCommon(unittest.TestCase):
    def test_common(self):
        pass

if __name__ == '__main__':
    unittest.main()
