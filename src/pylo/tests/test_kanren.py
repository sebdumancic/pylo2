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


def test_kanren():
    test = KanrenTest()

    test.simple_grandparent()
    test.graph_connectivity()

    print("all tests done!")

test_kanren()