
engines = []
try:
    from .GnuProlog import GNUProlog
    engines += ['GNUProlog']
except Exception:
    pass

try:
    from .XSBProlog import XSBProlog
    engines += ['XSBProlog']
except Exception:
    pass

try:
    from .SWIProlog import SWIProlog
    engines += ['SWIProlog']
except Exception:
    pass

__all__ = engines
# __all__ = [
#     'GNUProlog',
#     'XSBProlog',
#     'SWIProlog'
# ]
