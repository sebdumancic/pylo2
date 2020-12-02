try:
    from .GnuProlog import GNUProlog
except Exception:
    pass

try:
    from .SWIProlog import SWIProlog
except Exception:
    pass

try:
    from .XSBProlog import XSBProlog
except Exception:
    pass

from .prologsolver import Prolog

