from typing import Union, Sequence

import kanren
from orderedset import OrderedSet

from pylo.language import KANREN_LOGPY
from pylo.language.kanren import Constant, Type, Variable, Predicate, Atom, Clause, c_const, \
    construct_recursive_rule
from ..lpsolver import LPSolver
from ...language.commons import Term


class MiniKanren(LPSolver):

    def __init__(self, knowledge_base=None, background_knowledge=None):
        self.variable_mapping = dict() # A mapping from a name to the pylo representation of predicate, functor, constant, ...
        super().__init__(KANREN_LOGPY, knowledge_base, background_knowledge)

    def declare_constant(self, elem_constant: Constant) -> None:
        self.add_variable_mapping(elem_constant)
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

    def add_variable_mapping(self, x: Union[Predicate, Term]):
        if isinstance(x, (Predicate, Term)):
            if x.get_name() not in self.variable_mapping:
                self.variable_mapping[x.get_name()] = x

    def assert_fact(self, fact: Atom) -> None:
        self.add_variable_mapping(fact.get_predicate())
        for term in fact.get_terms():
            self.add_variable_mapping(term)

        kanren.fact(
            fact.get_predicate().as_kanren(),
            *[x.as_kanren() if getattr(x, "as_kanren", None) else x for x in fact.get_terms()]
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

    def asserta(self, clause: Union[Atom, Clause, Sequence[Clause]]):
        if isinstance(clause, Atom):
            self.assert_fact(clause)
        else:
            self.assert_rule(clause)

    def assertz(self,  clause: Union[Atom, Clause, Sequence[Clause]]):
        self.asserta(clause)

    def _query(self, num_solutions, *atoms: Atom):
        # find variables
        vars = OrderedSet()
        for atom in atoms:
            for var in atom.get_variables():
                if var not in vars:
                    vars.add(var)

        if len(vars) == 0:
            for atom in atoms:
                for term in atom.get_terms():
                    if term not in vars:
                        vars.add(term)

        ori_vars = list(vars)
        vars = [x.as_kanren() if getattr(x, "as_kanren", None) else x for x in ori_vars]
        goals = [x.as_kanren() if getattr(x, "as_kanren", None) else x for x in atoms]

        return kanren.run(num_solutions, vars, *goals), ori_vars

    def has_solution(self, *query: Union[Atom]):
        res, _ = self._query(1, *query)

        return True if res else False

    def query(self, *query, **kwargs):
        if 'max_solutions' in kwargs:
            max_solutions = kwargs['max_solutions']
        else:
            max_solutions = 0

        results, vars = self._query(max_solutions, *query)

        if len(results) == 0:
            return []

        def get_variable_mapping(x):
            if isinstance(x, str):
                return self.variable_mapping[x]
            elif isinstance(x, (kanren.Relation, kanren.Var)):
                return self.variable_mapping[x.name]
            else:
                return x

        return [
            dict(zip(
                    vars,
                    [get_variable_mapping(x) for x in result]
            )) for result in results
        ]


