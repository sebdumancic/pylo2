from pylo.language.commons import c_functor, List
from pylo.language.kanren import c_var, c_pred, c_const
from pylo.engines.kanren import MiniKanren


class KanrenTest:
    def simple_grandparent(self):
        p1 = c_const("p1")
        p2 = c_const("p2")
        p3 = c_const("p3")

        parent = c_pred("parent", 2)
        grandparent = c_pred("grandparent", 2)

        f1 = parent(p1, p2)
        f2 = parent(p2, p3)

        v1 = c_var("X")
        v2 = c_var("Y")
        v3 = c_var("Z")

        cl = grandparent(v1, v3) <= parent(v1, v2) & parent(v2, v3)

        solver = MiniKanren()

        solver.assert_fact(f1)
        solver.assert_fact(f2)
        solver.assert_rule(cl)

        # assert solver.has_solution(parent(v1, v2))
        # assert not solver.has_solution(parent(v1, v1))
        # assert len(solver.all_solutions(parent(v1, v2))) == 2
        # assert len(solver.all_solutions(parent(p1, v1))) == 1
        # assert solver.has_solution(parent(p1, p2))
        # assert not solver.has_solution(parent(p2, p1))
        # assert len(solver.one_solution(parent(p1, v1))) == 1
        #
        # assert solver.has_solution(grandparent(v1, v2))
        # assert solver.has_solution(grandparent(p1, v1))
        # assert len(solver.one_solution(grandparent(p1, v1))) == 1
        # assert solver.has_solution(grandparent(p1, p3))
        # assert not solver.has_solution(grandparent(p2, v1))
        # assert len(solver.one_solution(grandparent(p1, v1))) == 1
        # ans = solver.one_solution(grandparent(p1, v1))
        # assert ans[v1] == p3
        # ans = solver.one_solution(grandparent(v1, v2))
        # assert ans[v1] == p1 and ans[v2] == p3
        #
        # assert solver.has_solution(cl)
        # ans = solver.one_solution(cl)
        # assert ans[v1] == p1 and ans[v3] == p3
        # assert len(solver.all_solutions(cl)) == 1

        assert solver.has_solution(parent(v1, v2))
        assert not solver.has_solution(parent(v1, v1))
        assert len(solver.query(parent(v1, v2))) == 2
        assert len(solver.query(parent(p1, v1))) == 1
        assert solver.has_solution(parent(p1, p2))
        assert not solver.has_solution(parent(p2, p1))
        assert len(solver.query(parent(p1, v1), max_solutions=1)) == 1

        assert solver.has_solution(grandparent(v1, v2))
        assert solver.has_solution(grandparent(p1, v1))
        assert len(solver.query(grandparent(p1, v1), max_solutions=1)) == 1
        assert solver.has_solution(grandparent(p1, p3))
        assert not solver.has_solution(grandparent(p2, v1))
        assert len(solver.query(grandparent(p1, v1), max_solutions=1)) == 1
        ans = solver.query(grandparent(p1, v1), max_solutions=1)[0]
        assert ans[v1] == p3
        ans = solver.query(grandparent(v1, v2), max_solutions=1)[0]
        assert ans[v1] == p1 and ans[v2] == p3

        assert solver.has_solution(*cl.get_literals())
        ans = solver.query(*cl.get_literals(), max_solutions=1)[0]
        assert ans[v1] == p1 and ans[v3] == p3
        assert len(solver.query(*cl.get_literals())) == 1

    def graph_connectivity(self):
        v1 = c_const("v1")
        v2 = c_const("v2")
        v3 = c_const("v3")
        v4 = c_const("v4")

        edge = c_pred("edge", 2)
        path = c_pred("path", 2)

        f1 = edge(v1, v2)
        f2 = edge(v1, v3)
        f3 = edge(v2, v4)

        X = c_var("X")
        Y = c_var("Y")
        Z = c_var("Z")

        cl1 = path(X, Y) <= edge(X, Y)
        cl2 = path(X, Y) <= edge(X, Z) & path(Z, Y)

        solver = MiniKanren()

        solver.assert_fact(f1)
        solver.assert_fact(f2)
        solver.assert_fact(f3)

        solver.assert_rule([cl1, cl2])

        # assert solver.has_solution(path(v1, v2))
        # assert solver.has_solution(path(v1, v4))
        # assert not solver.has_solution(path(v3, v4))
        #
        # assert len(solver.one_solution(path(v1, X))) == 1
        # assert len(solver.one_solution(path(X, v4))) == 1
        # assert len(solver.one_solution(path(X, Y))) == 2
        #
        # assert len(solver.all_solutions(path(v1, X))) == 3
        # assert len(solver.all_solutions(path(X, Y))) == 4

        assert solver.has_solution(path(v1, v2))
        assert solver.has_solution(path(v1, v4))
        assert not solver.has_solution(path(v3, v4))

        assert len(solver.query(path(v1, X), max_solutions=1)[0]) == 1
        assert len(solver.query(path(X, v4), max_solutions=1)[0]) == 1
        assert len(solver.query(path(X, Y), max_solutions=1)[0]) == 2

        assert len(solver.query(path(v1, X))) == 3
        assert len(solver.query(path(X, Y))) == 4

    def various_queries(self):

        f = c_functor("t", 3)

        solver = MiniKanren()
        p = c_pred("p", 2)
        f1 = p("a", "b")
        solver.assertz(f1)

        X = c_var("X")
        Y = c_var("Y")

        query = p(X, Y)

        r = solver.has_solution(query)
        # print("has solution", r)
        assert r == True

        rv = solver.query(query)
        # print("all solutions", rv)
        assert len(rv) == 1

        f2 = p("a", "c")
        solver.assertz(f2)

        rv = solver.query(query)
        # print("all solutions after adding f2", rv)
        assert len(rv) == 2

        func1 = f(1, 2, 3)
        f3 = p(func1, "b")
        solver.assertz(f3)

        rv = solver.query(query)
        # print("all solutions after adding structure", rv)
        assert len(rv) == 3

        l = List([1, 2, 3, 4, 5])

        r = c_pred("r", 2)
        f4 = r("a", l)
        f5 = r("a", "b")

        solver.asserta(f4)
        solver.asserta(f5)

        query3 = r(X, Y)
        rv = solver.query(query3)
        assert len(rv) == 2

    def list_test(self):
        solver = MiniKanren()
        pred = c_pred("p", 2)
        f = pred(c_const("a"), List([1, 2, 3]))
        solver.asserta(f)
        query = pred(c_var("Y"), List([1, 2, c_var("X")]))
        r = solver.query(query)
        print(r)

    def variables_test(self):
        l = List([c_var("C"), List([c_var("D")])])
        p = c_pred("a", 2)
        pp = p(c_var("A"), l)
        assert [var.get_name() for var in pp.get_variables()] == ["A", "C", "D"]

    def fact_test(self):
        solver = MiniKanren()
        p = c_pred("p", 2)
        solver.assertz(p(1, 1))
        a = c_const("a")
        b = c_const("b")
        c = c_const("c")
        solver.assertz(p(a, b))

        assert solver.has_solution(p(1, 1))
        assert not solver.has_solution(p(1, 2))
        assert solver.has_solution(p(a, b))
        assert not solver.has_solution(p(b, a))
        assert not solver.has_solution(p(a, c))



def test_kanren():
    test = KanrenTest()


    test.simple_grandparent()
    test.graph_connectivity()
    test.various_queries()
    test.list_test()
    test.variables_test()
    test.fact_test()

    print("all tests done!")

test_kanren()