from functools import reduce
from math import log, ceil
from typing import Union

from z3 import (
    Fixedpoint,
    BitVecSort,
    Const,
    BoolSort,
    Function,
    BitVecVal,
    is_and,
    is_or,
    is_false,
)

from pylo.language import MUZ
from pylo.language.commons import Context
from pylo.language.datalog import (
    Type,
    Constant,
    Variable,
    Predicate,
    Atom,
    Clause,
    c_id_to_const,
    Not
)
from .datalogsolver import DatalogSolver


class MuZ(DatalogSolver):
    """
    Z3's muZ (datalog engine)

    Arguments:
        knowledge_base (default: None): facts to use
                                        Not supported yet
        background_knowledge (default: None): background knowledge (clauses)
                                              Not supported yet
        ctx [Context] (default: global context): context to use
    """

    def __init__(
            self, knowledge_base=None, background_knowledge=None, ctx: Context = None
    ):
        self._solver = Fixedpoint()
        self._solver.set(engine="datalog")
        super().__init__(MUZ, knowledge_base, background_knowledge, ctx)

    def declare_type(self, elem_type: Type):
        s = BitVecSort(ceil(log(len(elem_type), 2)))
        elem_type.add_engine_object(s)

    def declare_constant(self, elem_constant: Constant):
        s = elem_constant.get_type().get_engine_obj(self._name)
        c = BitVecVal(elem_constant.id(), s)
        elem_constant.add_engine_object(c)

    def declare_variable(self, elem_variable: Variable):
        s = elem_variable.get_type().get_engine_obj(self._name)
        v = Const(elem_variable.name, s)
        self._solver.declare_var(v)
        elem_variable.add_engine_object(v)

    def declare_predicate(self, elem_predicate: Predicate):
        arg_types = [
            x.get_engine_obj(self._name) for x in elem_predicate.get_arg_types()
        ]
        arg_types += [BoolSort()]
        rel = Function(elem_predicate.get_name(), *arg_types)
        self._solver.register_relation(rel)
        elem_predicate.add_engine_object(rel)

    def assert_fact(self, fact: Atom):
        self._solver.fact(fact.as_muz())

    def assert_rule(self, rule: Clause):
        cl_muz = rule.as_muz()
        self._solver.rule(cl_muz[0], cl_muz[1])

    def asserta(self, clause: Union[Atom, Clause]):
        if isinstance(clause, Atom):
            self.assert_fact(clause)
        else:
            self.assert_rule(clause)

    def assertz(self, clause: Union[Atom, Clause]):
        self.asserta(clause)

    def has_solution(self, *query: Union[Atom, Not]):
        body_atms = [x.as_muz() for x in query]
        res = self._solver.query(*body_atms)
        return True if res.r == 1 else False

    def query(self, *query, **kwargs):
        if 'max_solutions' in kwargs:
            max_solutions = kwargs['max_solutions']
        else:
            max_solutions = -1

        body_atms = [x.as_muz() for x in query]
        self._solver.query(*body_atms)

        ans = self._solver.get_answer()

        query_vars = [x.get_variables() for x in query]
        query_vars = reduce(lambda x, y: x + [v for v in y if v not in x], query_vars, [])

        if is_false(ans):
            # no solution
            return []
        elif not (is_and(ans) or is_or(ans)):
            # single solution, value of a single variable
            val = int(ans.children()[1].as_long())
            #varb = query.get_variables()[0]
            varb = query_vars[0]
            return [{varb: c_id_to_const(val, varb.get_type())}]
        elif is_or(ans) and not (
                is_and(ans.children()[0]) or is_or(ans.children()[0])
        ):
            # multiple solutions of single variable
            vals = [int(x.children()[1].as_long()) for x in ans.children()]
            #varbs = query.get_variables()[0]
            varbs = query_vars[0]
            varbs = [varbs] * len(vals)
            return [
                {k: c_id_to_const(v, varbs[0].get_type())}
                for k, v in zip(varbs, vals)
            ]
        elif is_and(ans):
            # single solution of more than 1 variable
            ans = [int(x.children()[1].as_long()) for x in ans.children()]
            ans = [ans]
        elif is_or(ans):
            # multiple solutions of more than 1 variable
            ans = ans.children()
            ans = [
                [int(y.children()[1].as_long()) for y in x.children()] for x in ans
            ]
        else:
            raise Exception(f"don't know how to parse {ans}")

        tmp_args = [v for x in query for v in x.get_variables()]
        args = reduce(lambda x, y: x + [y] if y not in x else x, tmp_args, [])

        answer = [
            dict(
                [
                    (v, c_id_to_const(c, v.get_type().name))
                    for v, c in zip(args, x)
                ]
            )
            for x in ans
        ]

        if max_solutions > 0:
            return answer[:max_solutions]
        else:
            return answer
