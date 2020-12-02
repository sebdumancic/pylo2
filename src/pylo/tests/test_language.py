from pylo.language.lp import c_var, c_pred, c_const, Predicate, Constant, Variable, Clause, Atom, Disjunction



class LanguageTest:

    def manual_constructs(self):
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

        assert isinstance(p1, Constant)
        assert isinstance(p2, Constant)
        assert isinstance(p3, Constant)

        assert isinstance(parent, Predicate)
        assert isinstance(grandparent, Predicate)

        assert isinstance(v1, Variable)
        assert isinstance(v2, Variable)
        assert isinstance(v2, Variable)

        assert isinstance(cl, Clause)

        assert isinstance(f1, Atom)
        assert isinstance(f2, Atom)

    def shorthand_constructs(self):
        parent = c_pred("parent", 2)
        grandparent = c_pred("grandparent", 2)

        f1 = parent("p1", "p2")
        f2 = parent("p2", "p3")
        f3 = grandparent("p1", "X")

        assert isinstance(parent, Predicate)
        assert isinstance(grandparent, Predicate)

        assert isinstance(f1, Atom)
        assert isinstance(f2, Atom)
        assert isinstance(f3, Atom)

        assert isinstance(f1.arguments[0], Constant)
        assert isinstance(f1.arguments[1], Constant)
        assert isinstance(f3.arguments[1], Variable)


def test_language():
    test = LanguageTest()
    test.manual_constructs()

    test.shorthand_constructs()

test_language()