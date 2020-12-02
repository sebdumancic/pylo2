from pylo.engines.prolog import GNUProlog
from pylo.language.lp import c_pred, c_functor, c_var, List

# from pylo.engines import GNUProlog
# from pylo import c_pred, c_functor, c_var, List


def gnu_test1(pl):
    #pl = GNUProlog()

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


def gnu_test5(solver):
    #solver = GNUProlog()

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


def all_gnu_tests():
    solver = GNUProlog()
    print("## TEST 1:")
    gnu_test1(solver)
    print("## TEST 2: ")
    gnu_test5(solver)

#all_gnu_tests()