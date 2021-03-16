# from src.pylo import (
#     Prolog
# )
from pylo.language.lp import Constant, Variable, Functor, Structure, List, Predicate, Atom, Not, Clause, \
    c_var, c_pred, c_functor, c_const, c_symbol, Pair
from pylo.engines.prolog.prologsolver import Prolog
#from pylo.language.lp import Variable, Structure, List, Atom, Clause, c_var, c_pred, c_functor, c_const, c_symbol
import sys

#sys.path.append("../../build")
import os
wrap_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(wrap_path + "/../../../build")

import pyxsb
from typing import Union
from functools import reduce


def _is_list(term: str):
    return term.startswith('[')


def _is_structure(term: str):
    first_bracket = term.find('(')

    if first_bracket == -1:
        return False
    else:
        tmp = term[:first_bracket]
        return all([x.isalnum() for x in tmp]) and tmp[0].isalpha()


def _pyxsb_string_to_const_or_var(term: str):
    if term[0].islower():
        return c_const(term)
    elif term.isnumeric():
        if '.' in term:
            return float(term)
        else:
            return int(term)
    else:
        return c_var(term)


def _extract_arguments_from_compound(term: str):
    if _is_list(term):
        term = term[1:-1]  # remove '[' and ']'
    else:
        first_bracket = term.find('(')
        term = term[first_bracket+1:-1] # remove outer brackets

    args = []
    open_brackets = 0
    last_open_char = 0
    for i in range(len(term)):
        char = term[i]
        if term[i] in ['(', '[']:
            open_brackets += 1
        elif term[i] in [')', ']']:
            open_brackets -= 1
        elif term[i] == ',' and open_brackets == 0:
            args.append(term[last_open_char:i])
            last_open_char = i + 1
        elif i == len(term) - 1:
            args.append(term[last_open_char:])
        else:
            pass

    return args


def _pyxsb_string_to_structure(term: str):
    first_bracket = term.find('(')
    functor = term[:first_bracket]
    args = [_pyxsb_string_to_pylo(x) for x in _extract_arguments_from_compound(term)]
    functor = c_symbol(functor, arity=len(args))

    return Structure(functor, args)


def _pyxsb_string_to_list(term: str):
    args = [_pyxsb_string_to_pylo(x) for x in _extract_arguments_from_compound(term)]
    return List(args)


def _pyxsb_string_to_pylo(term: str):
    if _is_list(term):
        return _pyxsb_string_to_list(term)
    elif _is_structure(term):
        return _pyxsb_string_to_structure(term)
    else:
        return _pyxsb_string_to_const_or_var(term)


class XSBProlog(Prolog):

    def __init__(self, exec_path=None):
        if exec_path is None:
            exec_path = os.getenv('XSB_HOME', None)
            raise Exception(f"Cannot find XSB_HOME environment variable")
        pyxsb.pyxsb_init_string(exec_path)
        super().__init__()

    def release(self):
        if not self.is_released:
            pyxsb.pyxsb_close()
            self.is_released: bool = True

    def __del__(self):
        self.release()

    def consult(self, filename: str):
        return pyxsb.pyxsb_command_string(f"consult('{filename}').")

    def use_module(self, module: str, **kwargs):
        assert 'predicates' in kwargs, "XSB Prolog: need to specify which predicates to import from module"
        predicates = kwargs['predicates']
        command = f"use_module({module},[{','.join([x.get_name() + '/' + str(x.get_arity()) for x in predicates])}])."
        return pyxsb.pyxsb_command_string(command)

    def asserta(self, clause: Union[Clause, Atom]):
        if isinstance(clause, Atom):
            query = f"asserta({clause})."
            return pyxsb.pyxsb_command_string(query)
        else:
            query = f"asserta(({clause}))."
            return pyxsb.pyxsb_command_string(query)

    def assertz(self, clause: Union[Atom, Clause]):
        if isinstance(clause, Atom):
            query = f"assertz({clause})."
            return pyxsb.pyxsb_command_string(query)
        else:
            query = f"assertz(({clause}))."
            return pyxsb.pyxsb_command_string(query)

    def retract(self, clause: Union[Atom, Clause]):
        if isinstance(clause, Atom):
            return pyxsb.pyxsb_command_string(f"retract({clause}).")
        else:
            return pyxsb.pyxsb_command_string(f"retract(({clause})).")

    def has_solution(self, *query: Atom):
        #assert not all([x.is_ground() for x in query]), "XSB Prolog currently cannot query ground queries"
        string_repr = ','.join([str(x) for x in query])
        res = pyxsb.pyxsb_query_string(f"{string_repr}.")

        if res:
            pyxsb.pyxsb_close_query()

        return True if res else False

    def query(self, *query, **kwargs):
        if 'max_solutions' in kwargs:
            max_solutions = kwargs['max_solutions']
        else:
            max_solutions = -1

        vars_of_interest = [[y for y in x.get_arguments() if isinstance(y, Variable)] for x in query]
        vars_of_interest = reduce(lambda x, y: x + y, vars_of_interest, [])
        vars_of_interest = reduce(lambda x, y: x + [y] if y not in x else x, vars_of_interest, [])

        string_repr = ','.join([str(x) for x in query])
        res = pyxsb.pyxsb_query_string(f"{string_repr}.")

        all_solutions = []
        while res and max_solutions != 0:
            vals = [x for x in res.strip().split(";")]
            var_assignments = [_pyxsb_string_to_pylo(x) for x in vals]
            all_solutions.append(dict([(v, s) for v, s in zip(vars_of_interest, var_assignments)]))

            res = pyxsb.pyxsb_next_string()
            max_solutions -= 1

        pyxsb.pyxsb_close_query()

        return all_solutions

    def register_foreign(self, pyfunction, arity):
        raise Exception("support for foreign predicates not supported yet")


if __name__ == '__main__':
    def test1():
        pl = XSBProlog("/Users/seb/Documents/programs/XSB")

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
        pl.use_module("lists", predicates=[member])

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

        q = c_pred("q", 2)
        cl = (q("X", "Y") <= r("X", "Y") & r("X", "Z"))

        pl.assertz(cl)
        query4 = q("X", "Y")
        rv = pl.query(query4)
        print("all solutions to q: ", rv)

        del pl


    def test2():
        pl = XSBProlog("/Users/seb/Documents/programs/XSB")

        person = c_pred("person", 1)
        friends = c_pred("friends", 2)
        stress = c_pred("stress", 1)
        influences = c_pred("influences", 2)
        smokes = c_pred("smokes", 1)
        asthma = c_pred("asthma", 1)

        pl.assertz(person("a"))
        pl.assertz(person("b"))
        pl.assertz(person("c"))
        pl.assertz(friends("a", "b"))
        pl.assertz(friends("a", "c"))

        pl.assertz(stress("X") <= person("X"))
        pl.assertz(influences("X", "Y") <= person("X") & person("Y"))
        pl.assertz(smokes("X") <= stress("X"))
        pl.assertz(smokes("X") <= friends("X", "Y") & influences("Y", "X") & smokes("Y"))
        pl.assertz(asthma("X") <= smokes("X"))

        query_p = person("X")
        tv = pl.query(query_p)
        print("all persons: ", tv)

        query_f = friends("X", "Y")
        tv = pl.query(query_f)
        print("all friends: ", tv)

        query_st = stress("Y")
        tv = pl.query(query_st)
        print("all stressed people: ", tv)

        tv = pl.query(influences("X", "Y"))
        print("all influences: ", tv)

        tv = pl.query(smokes("X"))
        print("all smokers: ", tv)

        tv = pl.query(asthma("X"))
        print("all asthma: ", tv)

        del pl

    def test3():
        pl = XSBProlog("/Users/seb/Documents/programs/XSB")

        bongard = c_pred('bongard', 2)
        circle = c_pred('circle', 2)
        inp = c_pred('in', 3)
        config = c_pred('config', 3)
        triangle = c_pred('triangle', 2)
        square = c_pred('square', 2)

        pl.assertz(bongard(2, "la"))
        pl.assertz(circle(2, "o3"))
        pl.assertz(config(2, "o1", "up"))
        pl.assertz(config(2, "o2", "up"))
        pl.assertz(config(2, "o5", "up"))
        pl.assertz(triangle(2, "o1"))
        pl.assertz(triangle(2, "o2"))
        pl.assertz(triangle(2, "o5"))
        pl.assertz(square(2, "o4"))
        pl.assertz(inp(2, "o4", "o5"))
        pl.assertz(inp(2, "o2", "o3"))

        A = c_var("A")
        B = c_var("B")
        C = c_var("C")
        D = c_var("D")

        #pl.assertz((bongard(A,"la") <= triangle(A,C) & inp(A, C, D)))

        res = pl.query(bongard(A, "la"), triangle(A,C), inp(A, C, D))

        print(res)

        del pl

    def test5():
        solver = XSBProlog("/Users/seb/Documents/programs/XSB")

        edge = c_pred("edge", 2)
        path = c_pred("path", 2)

        f1 = edge("v1", "v2")
        f2 = edge("v1", "v3")
        f3 = edge("v2", "v4")

        X = c_var("X")
        Y = c_var("Y")
        Z = c_var("Z")

        cl1 = (path("X", "Y") <= edge("X", "Y"))
        cl2 = (path("X", "Y") <= edge("X", "Z") & path("Z", "Y"))

        as1 = solver.assertz(f1)
        as2 = solver.assertz(f2)
        as3 = solver.assertz(f3)

        as4 = solver.assertz(cl1)
        solver.assertz(cl2)

        assert solver.has_solution(edge("X", "v2"))
        assert solver.has_solution(path("v1", "v4"))
        assert len(solver.query(path("v1", "X"), max_solutions=1)[0]) == 1
        assert len(solver.query(path(X, "v4"), max_solutions=1)[0]) == 1
        assert len(solver.query(path(X, Y), max_solutions=1)[0]) == 2

        assert len(solver.query(path("v1", X))) == 3
        assert len(solver.query(path(X, Y))) == 4

        solver.assertz(edge("v4", "v5"))
        assert len(solver.query(path(X, Y))) == 7

        print(solver.query(edge(X, Y), edge(Y, Z), edge(Z,"W")))

        del solver

    def test6():
        solver = XSBProlog("/Users/seb/Documents/programs/XSB")

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
    test6()

