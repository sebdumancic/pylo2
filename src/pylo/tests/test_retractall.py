from pylo.engines.prolog import (
    SWIProlog, 
    # GNUProlog, 
    XSBProlog
)
from pylo.language.lp import c_pred, c_functor, c_var, List, c_const

def test(pl):
    pred1 = c_pred("pred1",1)
    pred2 = c_pred("pred2",1)

    const1 = c_const("const1")
    const2 = c_const("const2")

    x = c_var("X")
    y = c_var("Y")

    atoms = [ pred1(const1),pred1(const2),pred2(const1),pred2(const2) ]
    for atom in atoms:
        pl.assertz(atom)

    q = pred1(x) # Should have 2 solutions: const1 and const2
    assert len(pl.query(q)) == 2

    pl.retract(atoms[0])    # q should have 1 solution: const
    print(len(pl.query(q)))
    assert len(pl.query(q)) == 1

    pl.retract_all()    # Empty engine: no result for query
    assert len(pl.query(pred1(x))) == 0
    assert len(pl.query(pred2(x))) == 0


swipl = SWIProlog()
test(swipl)

xsb = XSBProlog()
test(xsb)

# gnu = GNUProlog()
# test(gnu)
