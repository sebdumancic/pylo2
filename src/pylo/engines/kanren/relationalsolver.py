from pylo.language.commons import Context
from ..lpsolver import LPSolver


class RelationalSolver(LPSolver):

    def __init__(self, name, knowledge_base=None, background_knowledge=None, ctx: Context = None):
        super().__init__(name, knowledge_base, background_knowledge, ctx)