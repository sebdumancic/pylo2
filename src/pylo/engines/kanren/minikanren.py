from typing import Union, Sequence

import kanren

from pylo.language import KANREN_LOGPY
from pylo.language.kanren import Constant, Type, Variable, Predicate, Atom, Clause, c_const, \
    construct_recursive_rule
from ..lpsolver import LPSolver


class MiniKanren(LPSolver):

    def __init__(self, knowledge_base=None, background_knowledge=None):
        super().__init__(KANREN_LOGPY, knowledge_base, background_knowledge)

    def declare_constant(self, elem_constant: Constant) -> None:
        elem_constant.add_engine_object(elem_constant.name)

    def declare_type(self, elem_type: Type) -> None:
        # No types in miniKanren
        pass

    def declare_variable(self, elem_variable: Variable) -> None:
        v = kanren.var()
        elem_variable.add_engine_object(v)

    def declare_predicate(self, elem_predicate: Predicate) -> None:
        # predicate declared once facts and rules are added
        #     predicates used as facts need to be declared as
        pass

    def assert_fact(self, fact: Atom) -> None:
        try:
            fact.get_predicate().get_engine_obj(KANREN_LOGPY)
        except Exception:
            fact.get_predicate().add_engine_object((KANREN_LOGPY, kanren.Relation()))

        kanren.fact(fact.get_predicate().get_engine_obj(KANREN_LOGPY),
                    *[x.as_kanren() for x in fact.get_terms()]
                    )

    def assert_rule(self, rule: Union[Clause, Sequence[Clause]]) -> None:
        # only needs to add a miniKanren object to the predicate in the head
        if isinstance(rule, Clause):
            if rule.is_recursive():
                raise Exception(f"recursive rule needs to be added together with the base base: {rule}")
            else:
                obj = rule.as_kanren()
                rule.get_head().get_predicate().add_engine_object((KANREN_LOGPY, obj))
        else:

            obj = construct_recursive_rule(rule)

            rule[0].get_head().get_predicate().add_engine_object((KANREN_LOGPY, obj))

    def _query(self, num_solutions, *atoms: Atom):
        # find variables
        vars = {}
        for atom in atoms:
            for v in atom.get_variables():
                if v not in vars:
                    vars[v] = len(vars)

        ori_vars = sorted(list(vars.keys()), key=lambda x: vars[x])
        vars = [x.as_kanren() for x in ori_vars]

        if len(vars) == 0:
            terms = {}
            for atom in atoms:
                for t in atom.get_terms():
                    if t not in terms:
                        terms[t] = len(terms)
            ori_vars = sorted(list(terms.keys()), key=lambda x: terms[x])
            ori_vars = [x.as_kanren() for x in ori_vars]

        goals = [x.as_kanren() for x in atoms]

        return kanren.run(num_solutions, vars, *goals), ori_vars

    def has_solution(self, *query: Union[Atom]):
        res, _ = self._query(1, *query)

        return True if res else False

    def query(self, *query, **kwargs):
        if 'max_solutions' in kwargs:
            max_solutions = kwargs['max_solutions']
        else:
            max_solutions = 0

        res, vars = self._query(max_solutions, *query)

        if len(res) == 0:
            return []

        return [
            dict(zip(vars, [c_const(y, vars[ind].get_type()) for ind, y in enumerate(x)])) for x in res
        ]


