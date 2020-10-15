from pylo.engines import SWIProlog

from pylo import global_context, List

def test1():
    pl = SWIProlog()

    p = global_context.get_predicate("p", 2)
    f = global_context.get_functor("t", 3)
    f1 = p("a", "b")

    pl.assertz(f1)

    X = global_context.get_variable("X")
    Y = global_context.get_variable("Y")

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

    member = global_context.get_predicate("member", 2)

    query2 = member(X, l)

    rv = pl.query(query2)
    print("all solutions to list membership ", rv)

    r = global_context.get_predicate("r", 2)
    f4 = r("a", l)
    f5 = r("a", "b")

    pl.asserta(f4)
    pl.asserta(f5)

    query3 = r(X, Y)

    rv = pl.query(query3)
    print("all solutions after adding list ", rv)

    del pl


def test2():
    pl = SWIProlog()

    bongard = global_context.get_predicate('bongard', 2)
    circle = global_context.get_predicate('circle', 2)
    inp = global_context.get_predicate('in', 3)
    config = global_context.get_predicate('config', 3)
    triangle = global_context.get_predicate('triangle', 2)
    square = global_context.get_predicate('square', 2)

    f1 = bongard(2, "la")
    f2 = circle(2, "o3")
    f3 = config(2, "o1", "up")
    f4 = config(2, "o2", "up")
    f5 = config(2, "o5", "up")
    f6 = triangle(2, "o1")
    f7 = triangle(2, "o2")
    f8 = triangle(2, "o5")
    f9 = square(2, "o4")
    f10 = inp(2, "o4", "o5")
    f11 = inp(2, "o2", "o3")

    A = global_context.get_variable("A")
    B = global_context.get_variable("B")
    C = global_context.get_variable("C")
    D = global_context.get_variable("D")

    res = pl.query(bongard(A, B), triangle(A, C), inp(A, C, D))

    print(res)

test2()
