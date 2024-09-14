import sys, os
sys.path.append(os.path.abspath('src'))

import unittest

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
