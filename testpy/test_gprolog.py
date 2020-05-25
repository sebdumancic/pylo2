import pygprolog

pygprolog.pygp_Start_Prolog()

a = pygprolog.pygp_Create_Allocate_Atom("a")
a_term = pygprolog.pygp_Mk_Atom(a)

b = pygprolog.pygp_Create_Allocate_Atom("b")
b_term = pygprolog.pygp_Mk_Atom(b)

p = pygprolog.pygp_Create_Allocate_Atom("p")

f = pygprolog.pygp_Mk_Compound(p, 2, [a_term, b_term])

ass_term = pygprolog.pygp_Find_Atom("assertz")
#assertion = pygprolog.pygp_Mk_Compound(ass_term, 1, [f])

pygprolog.pygp_Query_Begin()

q_Var1 = pygprolog.pygp_Query_Call(ass_term, 1, [f])

pygprolog.pygp_Query_End()


pygprolog.pygp_Query_Begin()

v1 = pygprolog.pygp_Mk_Variable()
v2 = pygprolog.pygp_Mk_Variable()

q_Var2 = pygprolog.pygp_Query_Call(p, 2, [v1, v2])

res = pygprolog.pygp_Query_Next_Solution()

pygprolog.pygp_Query_End()

pygprolog.pygp_Stop_Prolog()