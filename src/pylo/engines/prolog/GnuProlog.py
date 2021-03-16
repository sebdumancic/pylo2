# from src.pylo.engines.prolog import Prolog
# from src.pylo.language.lp import Constant, Variable, Functor, Structure, List, Atom, Not, Clause, \
#    c_const, c_pred, c_var, c_functor, c_symbol

from pylo.engines.prolog.prologsolver import Prolog
from pylo.language.lp import Constant, Variable, Functor, Structure, List, Atom, Not, Clause, \
    c_const, c_pred, c_var, c_functor, c_symbol, Pair

import sys
sys.path.append("../../../build")

import pygprolog
from typing import Union, Dict
from functools import reduce


def _const_to_pygp(c: Constant):
    return pygprolog.pygp_Mk_Atom(
        pygprolog.pygp_Create_Allocate_Atom(c.get_name())
    )


def _var_to_pygp(v: Variable, lit_var_store: Dict[Variable, int]):
    if v in lit_var_store:
        return lit_var_store[v]
    else:
        tmpV = pygprolog.pygp_Mk_Variable()
        lit_var_store[v] = tmpV
        return tmpV


def _num_to_pygp(value: Union[int, float]):
    if isinstance(value, int):
        return pygprolog.pygp_Mk_Integer(value)
    else:
        return pygprolog.pygp_Mk_Float(value)


def _functor_to_pygp(func: Functor):
    intKey = pygprolog.pygp_Find_Atom(func.get_name())

    if intKey == -1:
        return pygprolog.pygp_Mk_Atom(func.get_name())
    else:
        return intKey


def _to_pygp(item, lit_var_store: Dict[Variable, int]):
    if isinstance(item, Constant):
        return _const_to_pygp(item)
    elif isinstance(item, Variable):
        return _var_to_pygp(item, lit_var_store)
    elif isinstance(item, (int, float)):
        return _num_to_pygp(item)
    elif isinstance(item, List):
        return _list_to_pygp(item, lit_var_store)
    elif isinstance(item, Pair):
        return _pair_to_pygp(item, lit_var_store)
    elif isinstance(item, Structure):
        return _structure_to_pygp(item, lit_var_store)
    else:
        raise Exception(f"don't know how to turn {item} ({type(item)}) to pygp")


def _list_to_pygp(ll: List, lit_var_store: Dict[Variable, int]):
    args = [_to_pygp(x, lit_var_store) for x in ll.get_arguments()]

    return pygprolog.pygp_Mk_List(args)


def _pair_to_pygp(p: Pair, lit_var_store: Dict[Variable, int]):
    left = _to_pygp(p.get_left(), lit_var_store)
    right = _to_pygp(p.get_right(), lit_var_store)

    functor = pygprolog.pygp_Find_Atom('.')
    if functor < 0:
        functor = pygprolog.pygp_Create_Allocate_Atom('.')

    args = [left, right]
    return pygprolog.pygp_Mk_Compound(functor, 2, args)


def _structure_to_pygp(struct: Structure, lit_var_store: Dict[Variable, int]):
    func = _functor_to_pygp(struct.get_functor())
    args = [_to_pygp(x, lit_var_store) for x in struct.get_arguments()]

    return pygprolog.pygp_Mk_Compound(func, struct.get_functor().get_arity(), args)


def _lit_to_pygp(literal: Atom, var_store=None):
    if var_store is None:
        var_store = {}
    pred = pygprolog.pygp_Find_Atom(literal.get_predicate().get_name())
    if pred < 0:
        pred = pygprolog.pygp_Create_Allocate_Atom(literal.get_predicate().get_name())
    args = [_to_pygp(x, var_store) for x in literal.get_arguments()]

    return pygprolog.pygp_Mk_Compound(pred, literal.get_predicate().get_arity(), args)


def _neg_to_pygp(negation: Not, var_store=None):
    if var_store is None:
        var_store = {}
    inner = _lit_to_pygp(negation.get_atom(), var_store)

    ng_f = pygprolog.pygp_Find_Atom("\\+")
    return pygprolog.pygp_Mk_Compound(ng_f, 1, [inner])


def _conjoin_lits(pyg_literals):
    conj_f = pygprolog.pygp_Find_Atom(",")
    return reduce(lambda x, y: pygprolog.pygp_Mk_Compound(conj_f, 2, [x, y]), pyg_literals)


def _cl_to_pygp(clause: Clause):
    var_store = {}
    head_pygp = _lit_to_pygp(clause.get_head(), var_store)
    body_pygp = [
        _lit_to_pygp(x, var_store) if isinstance(x, Atom) else _neg_to_pygp(x, var_store)
        for x in clause.get_body().get_literals()
    ]
    # conj_f = pygprolog.pygp_Find_Atom(",")
    # body_pygp = reduce(lambda x, y: pygprolog.pygp_Mk_Compound(conj_f, 2, [x, y]), body_pygp)
    body_pygp = _conjoin_lits(body_pygp)
    cl_f = pygprolog.pygp_Find_Atom(":-")

    return pygprolog.pygp_Mk_Compound(cl_f, 2, [head_pygp, body_pygp])


def _pygp_to_const(term):
    # global global_context
    return c_const(pygprolog.pygp_Rd_String(term))


def _pygp_atm_to_symbol(term):
    # global global_context
    return c_symbol(pygprolog.pygp_Rd_String(term))


def _pygp_to_number(term):
    if pygprolog.pygp_Type_Of_Term(term) == 3:
        return int(pygprolog.pygp_Rd_Integer(term))
    elif pygprolog.pygp_Type_Of_Term(term) == 4:
        return float(pygprolog.pygp_Rd_Decimal(term))
    else:
        raise Exception(f"term type {pygprolog.pygp_Type_Of_Term(term)} is not a number")


def _pygp_to_list(term):
    elems = pygprolog.pygp_Rd_List(term)
    elems = [_read_pygp(x) for x in elems]

    return List(elems)


def _pygp_to_structure(term):
    v1 = pygprolog.pygp_Mk_Variable()
    v2 = pygprolog.pygp_Mk_Variable()

    pygprolog.pygp_Builtin_Functor(term, v1, v2)

    functor = pygprolog.pygp_Rd_String(v1)
    arity = pygprolog.pygp_Rd_Integer(v2)
    args = []
    for i in range(1, arity+1):
        v = pygprolog.pygp_Mk_Variable()
        pygprolog.pygp_Builtin_Arg(pygprolog.pygp_Mk_Integer(i), term, v)
        args.append(_read_pygp(v))

    # global global_context

    return Structure(c_functor(functor, arity), args)


def _read_pygp(term, pygp_term_to_var={}):
    term_type = pygprolog.pygp_Type_Of_Term(term)

    if term_type == 1:
        if term in pygp_term_to_var:
            return pygp_term_to_var[term]
        else:
            all_var_names = set([x.get_name() for x in pygp_term_to_var.values()])
            new_name = [chr(x) for x in range(ord('A'), ord('Z') + 1) if chr(x) not in all_var_names][0]
            if len(new_name) == 0:
                new_name = [f"{chr(x)}{chr(y)}" for x in range(ord('A'), ord('Z')+1) for y in range(ord('A'), ord('Z')+1) if f"{chr(x)}{chr(y)}" not in all_var_names]
            return Variable(new_name)
            # global global_context
            # return global_context.get_variable(all_names)
    elif term_type == 3 or term_type == 4:
        return _pygp_to_number(term)
    elif term_type == 5:
        return _pygp_atm_to_symbol(term)
    elif term_type == 6:
        return _pygp_to_list(term)
    else:
        return _pygp_to_structure(term)


class GNUProlog(Prolog):

    def __init__(self):
        pygprolog.pygp_Start_Prolog()
        super().__init__()

    def release(self):
        if not self.is_released:
            pygprolog.pygp_Stop_Prolog()
            self.is_released: bool = True

    def __del__(self):
        self.release()

    def consult(self, filename):
        consult = pygprolog.pygp_Find_Atom("consult")
        arg = pygprolog.pygp_Mk_String(filename)

        pygprolog.pygp_Query_Begin()
        q_Var1 = pygprolog.pygp_Query_Call(consult, 1, [arg])
        pygprolog.pygp_Query_End()

        return q_Var1

    def use_module(self, module: str, **kwargs):
        raise Exception(f"GNUProlog does not have modules.")

    def _asserta_lit(self, literal: Atom):
        pl = _lit_to_pygp(literal)
        asa_p = pygprolog.pygp_Find_Atom("asserta")

        pygprolog.pygp_Query_Begin()
        q_Var1 = pygprolog.pygp_Query_Call(asa_p, 1, [pl])
        pygprolog.pygp_Query_End()

        return q_Var1

    def _asserta_cl(self, clause: Clause):
        clp = _cl_to_pygp(clause)

        asa_p = pygprolog.pygp_Find_Atom("asserta")

        pygprolog.pygp_Query_Begin()
        q_Var1 = pygprolog.pygp_Query_Call(asa_p, 1, [clp])
        pygprolog.pygp_Query_End()

        return q_Var1

    def asserta(self, clause: Union[Atom, Clause]):
        if isinstance(clause, Atom):
            return self._asserta_lit(clause)
        else:
            return self._asserta_cl(clause)

    def _assertz_lit(self, literal: Atom):
        pl = _lit_to_pygp(literal)
        asa_p = pygprolog.pygp_Find_Atom("assertz")

        pygprolog.pygp_Query_Begin()
        q_Var1 = pygprolog.pygp_Query_Call(asa_p, 1, [pl])
        pygprolog.pygp_Query_End()

        return q_Var1

    def _assertz_cl(self, clause: Clause):
        clp = _cl_to_pygp(clause)

        asa_p = pygprolog.pygp_Find_Atom("assertz")

        pygprolog.pygp_Query_Begin()
        q_Var1 = pygprolog.pygp_Query_Call(asa_p, 1, [clp])
        pygprolog.pygp_Query_End()

        return q_Var1

    def assertz(self, clause: Union[Atom, Clause]):
        if isinstance(clause, Atom):
            return self._assertz_lit(clause)
        else:
            return self._assertz_cl(clause)

    def _retract_lit(self, literal: Atom):
        pl = _lit_to_pygp(literal)
        asa_p = pygprolog.pygp_Find_Atom("retract")

        pygprolog.pygp_Query_Begin()
        q_Var1 = pygprolog.pygp_Query_Call(asa_p, 1, [pl])
        pygprolog.pygp_Query_End()

        return q_Var1

    def _retract_cl(self, clause: Clause):
        clp = _cl_to_pygp(clause)

        asa_p = pygprolog.pygp_Find_Atom("retract")

        pygprolog.pygp_Query_Begin()
        q_Var1 = pygprolog.pygp_Query_Call(asa_p, 1, [clp])
        pygprolog.pygp_Query_End()

        return q_Var1

    def retract(self, clause: Union[Atom, Clause]):
        if isinstance(clause, Atom):
            return self._retract_lit(clause)
        if isinstance(clause, Clause):
            return self._retract_cl(clause)

    def has_solution(self, *query: Union[Atom, Not]):
        var_store = {}

        if len(query) == 1:
            query = query[0]
            args = [_to_pygp(x, var_store) for x in query.get_arguments()]
            func = pygprolog.pygp_Find_Atom(query.get_predicate().get_name())

            pygprolog.pygp_Query_Begin()
            q_Var1 = pygprolog.pygp_Query_Call(func, query.get_predicate().get_arity(), args)
            pygprolog.pygp_Query_End()

            return True if q_Var1 == 1 else False

        else:
            first_elem = _lit_to_pygp(query[0], var_store)
            rest = [
                _lit_to_pygp(x, var_store) if isinstance(x, Atom) else _neg_to_pygp(x, var_store)
                for x in query[1:]
            ]
            rest = _conjoin_lits(rest)

            pygprolog.pygp_Query_Begin()
            conjf = pygprolog.pygp_Find_Atom(",")

            q_Var = pygprolog.pygp_Query_Call(conjf, 2, [first_elem, rest])

            pygprolog.pygp_Query_End()

            return True if q_Var == 1 else False

    def query(self, *query, **kwargs):
        if 'max_solutions' in kwargs:
            max_solutions = kwargs['max_solutions']
        else:
            max_solutions = -1

        vars_of_interest = [[y for y in x.get_arguments() if isinstance(y, Variable)] for x in query]
        vars_of_interest = reduce(lambda x, y: x + y, vars_of_interest, [])
        vars_of_interest = reduce(lambda x, y: x + [y] if y not in x else x, vars_of_interest, [])
        var_store = dict([(x, pygprolog.pygp_Mk_Variable()) for x in vars_of_interest])

        pygprolog.pygp_Query_Begin()

        if len(query) == 1:
            query = query[0]
            f = pygprolog.pygp_Find_Atom(query.get_predicate().get_name())
            args = [_to_pygp(x, var_store) for x in query.get_arguments()]
            res = pygprolog.pygp_Query_Call(f, len(args), args)
        else:
            first = _lit_to_pygp(query[0], var_store)
            rest = [
                _lit_to_pygp(x, var_store) if isinstance(x, Atom) else _neg_to_pygp(x, var_store)
                for x in query[1:]
            ]
            rest = _conjoin_lits(rest)
            conjf = pygprolog.pygp_Find_Atom(",")

            res = pygprolog.pygp_Query_Call(conjf, 2, [first, rest])

        # discover all solutions
        all_solutions = []

        while res and max_solutions != 0:
            tmp_solution = {}
            for vn in var_store:
                tmp_solution[vn] = _read_pygp(var_store[vn])

            res = pygprolog.pygp_Query_Next_Solution()
            max_solutions -= 1
            all_solutions.append(tmp_solution)

        pygprolog.pygp_Query_End()

        return all_solutions

    def register_foreign(self, pyfunction, arity):
        raise Exception("support for foreign predicate not implemented yet")


if __name__ == '__main__':

    def test1():
        pl = GNUProlog()

        p = c_pred("p", 2)
        f = c_functor("t", 3)
        f1 = p("a", "b")

        pl.assertz(f1)

        X = c_var("X")
        Y = c_var("Y")

        query = p(X, Y)

        r = pl.has_solution(query)
        print("has solution", r)

        rv = pl.query(query)
        print("all solutions", rv)

        f2 = p("a", "c")
        pl.assertz(f2)

        rv = pl.query(query)
        print("all solutions after adding f2", rv)

        func1 = f(1, 2, 3)
        f3 = p(func1, "b")
        pl.assertz(f3)

        rv = pl.query(query)
        print("all solutions after adding structure", rv)

        l = List([1, 2, 3, 4, 5])

        member = c_pred("member", 2)

        query2 = member(X, l)

        rv = pl.query(query2)
        print("all solutions to list membership ", rv)

        r = c_pred("r", 2)
        f4 = r("a", l)
        f5 = r("a", "b")

        pl.asserta(f4)
        pl.asserta(f5)

        query3 = r(X, Y)

        rv = pl.query(query3)
        print("all solutions after adding list ", rv)

        del pl

    def test5():
        solver = GNUProlog()

        edge = c_pred("edge", 2)
        path = c_pred("path", 2)

        f1 = edge("v1", "v2")
        f2 = edge("v1", "v3")
        f3 = edge("v2", "v4")

        X = c_var("X")
        Y = c_var("Y")
        Z = c_var("Z")

        cl1 = path(X, Y) <= edge(X, Y)
        cl2 = path(X, Y) <= edge(X, Z) & path(Z, Y)

        solver.assertz(f1)
        solver.assertz(f2)
        solver.assertz(f3)

        solver.assertz(cl1)
        solver.assertz(cl2)

        assert solver.has_solution(path("v1", "v2"))
        assert solver.has_solution(path("v1", "v4"))
        assert not solver.has_solution(path("v3", "v4"))

        assert len(solver.query(path("v1", X), max_solutions=1)[0]) == 1
        assert len(solver.query(path(X, "v4"), max_solutions=1)[0]) == 1
        assert len(solver.query(path(X, Y), max_solutions=1)[0]) == 2

        assert len(solver.query(path("v1", X))) == 3
        assert len(solver.query(path(X, Y))) == 4

        solver.assertz(edge("v4", "v5"))
        assert len(solver.query(path(X, Y))) == 7

        print(solver.query(edge(X, Y), edge(Y, Z), edge(Z,"W")))
        del solver

    def test6():
        solver = GNUProlog()

        head = c_pred("head", 2)
        tail = c_pred("tail", 2)
        take_second = c_pred("take_second", 2)
        H = c_var("Head")
        T = c_var("Tail")
        X = c_var("X")
        Y = c_var("Y")

        hatm1 = head(Pair(H, T), H)
        tatm1 = tail(Pair(H, T), T)
        cl = (take_second(X,Y) <= tail(X, T) & head(T, Y))

        solver.assertz(hatm1)
        solver.assertz(tatm1)
        solver.assertz(cl)

        l = List([1, 2, 3, 4, 5])
        print(solver.query(take_second(l, X)))

        del solver

    #test1()
    #test5()

    #test6()





