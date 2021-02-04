
from pylo.engines import GNUProlog

from pylo.language.lp import global_context, List


pl = GNUProlog()

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

