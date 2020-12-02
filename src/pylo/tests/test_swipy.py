# from pylo.engines import SWIProlog
# from pylo import c_pred, c_functor, c_var, List

from pylo.engines.prolog import SWIProlog
from pylo.language.lp import c_pred, c_functor, c_var, List


def swipl_test1():
    pl = SWIProlog()

    p = c_pred("p", 2)
    f = c_functor("t", 3)
    f1 = p("a", "b")

    pl.assertz(f1)

    X = c_var("X")
    Y = c_var("Y")

    query = p(X, Y)

    r = pl.has_solution(query)
    #print("has solution", r)
    assert r == True

    rv = pl.query(query)
    #print("all solutions", rv)
    assert len(rv) == 1

    f2 = p("a", "c")
    pl.assertz(f2)

    rv = pl.query(query)
    #print("all solutions after adding f2", rv)
    assert len(rv) == 2

    func1 = f(1, 2, 3)
    f3 = p(func1, "b")
    pl.assertz(f3)

    rv = pl.query(query)
    #print("all solutions after adding structure", rv)
    assert len(rv) == 3

    l = List([1, 2, 3, 4, 5])

    member = c_pred("member", 2)

    query2 = member(X, l)

    rv = pl.query(query2)
    #print("all solutions to list membership ", rv)
    assert len(rv) == 5

    r = c_pred("r", 2)
    f4 = r("a", l)
    f5 = r("a", "b")

    pl.asserta(f4)
    pl.asserta(f5)

    query3 = r(X, Y)

    rv = pl.query(query3)
    #print("all solutions after adding list ", rv)
    assert len(rv) == 2

    # Foreign predicates

    # def hello(t):
    #     print("Foreign: Hello", t)
    #
    # hello_pred = pl.register_foreign(hello, 1)
    # # print(hello_pred)
    #
    # f_query = hello_pred("a")
    #
    # pl.has_solution(f_query)
    #
    del pl


def swipl_test2():
    pl = SWIProlog()

    bongard = c_pred('bongard', 2)
    circle = c_pred('circle', 2)
    inp = c_pred('in', 3)
    config = c_pred('pconfig', 3)
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
    # pl.assertz(square(2, "o4"))
    pl.assertz(inp(2, "o4", "o5"))
    pl.assertz(inp(2, "o2", "o3"))

    A = c_var("A")
    B = c_var("B")
    C = c_var("C")
    D = c_var("D")

    #pl.assertz((bongard(A,"la") <= triangle(A,C) & inp(A, C, D)))

    res = pl.query(bongard(A, "la"), triangle(A,C), inp(A, C, D))

    #print(res)
    assert len(res) == 1

    del pl


def swipl_test4():
    pl = SWIProlog()

    parent = c_pred("parent", 2)
    grandparent = c_pred("grandparent", 2)

    f1 = parent("p1", "p2")
    f2 = parent("p2", "p3")

    v1 = c_var("X")
    v2 = c_var("Y")
    v3 = c_var("Z")

    cl = (grandparent(v1, v3) <= parent(v1, v2) & parent(v2, v3))

    pl.assertz(f1)
    pl.assertz(f2)
    pl.assertz(cl)

    assert pl.has_solution(parent(v1, v2))
    assert not pl.has_solution(parent(v1, v1))
    assert len(pl.query(parent(v1, v2))) == 2
    assert len(pl.query(parent("p1", v1))) == 1
    assert pl.has_solution(parent("p1", "p2"))
    assert not pl.has_solution(parent("p2", "p1"))
    assert len(pl.query(parent("p1", v1), max_solutions=1)) == 1

    assert pl.has_solution(grandparent(v1, v2))
    assert pl.has_solution(grandparent("p1", v1))
    assert len(pl.query(grandparent("p1", v1), max_solutions=1)) == 1

    assert len(pl.query(grandparent(v1, v2))) == 1

    pl.assertz(parent("p2", "p4"))
    pl.assertz(parent("p1", "p5"))
    assert len(pl.query(grandparent(v1, v2))) == 2

    del pl


def swipl_test5():
    solver = SWIProlog()

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

    #print(solver.query(edge(X, Y), edge(Y, Z), edge(Z,"W")))
    del solver


def all_swipl_tests():
    print("## TEST 1:")
    swipl_test1()
    print("## TEST 2: ")
    swipl_test2()
    print("## TEST 3: ")
    swipl_test4()
    print("## TEST 4: ")
    swipl_test5()

#all_swipl_tests()

