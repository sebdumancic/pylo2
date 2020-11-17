from .test_gnuprolog import all_gnu_tests
from .test_swipy import all_swipl_tests
from .test_xsb import all_xsb_tests
from .test_kanren import test_kanren
from .test_datalog import test_datalog
from .test_language import test_language

__all__ = [
    'all_gnu_tests',
    'all_xsb_tests',
    'all_swipl_tests',
    'test_kanren',
    'test_datalog',
    'test_language'
]