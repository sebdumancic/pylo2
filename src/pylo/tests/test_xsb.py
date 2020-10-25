# from pylo.engines import XSBProlog
# from pylo import c_pred, c_functor, c_var, List
from ..engines import XSBProlog
from .. import c_pred, c_functor, c_var, List


# "/Users/seb/Documents/programs/XSB"
def xsb_test1(path):
    pl = XSBProlog(path)

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


def xsb_test2(path):
    pl = XSBProlog(path)

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


def xsb_test3(path):
    pl = XSBProlog(path)

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


def xsb_test5(path):
    solver = XSBProlog(path)

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


def all_xsb_tests(path):
    xsb_test1(path)
    xsb_test2(path)
    xsb_test3(path)
    xsb_test5(path)


#all_xsb_tests("/Users/seb/Documents/programs/XSB")

