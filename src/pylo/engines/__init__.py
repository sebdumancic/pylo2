engines = ['Prolog']
try:
    from pylo.engines.prolog.GnuProlog import GNUProlog
    engines += ['GNUProlog']
except Exception:
    pass

try:
    from pylo.engines.prolog.XSBProlog import XSBProlog
    engines += ['XSBProlog']
except Exception:
    pass

try:
    from pylo.engines.prolog.SWIProlog import SWIProlog
    engines += ['SWIProlog']
except Exception:
    pass

try:
    from pylo.engines.datalog import muz
    engines += ['muz']
except Exception:
    pass


from pylo.engines.kanren import MiniKanren
engines += ['MiniKanren']

__all__ = engines
# __all__ = [
#     'GNUProlog',
#     'XSBProlog',
#     'SWIProlog'
# ]
