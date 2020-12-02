from functools import reduce
from typing import Sequence

import kanren

from ..commons import Clause, Variable


def _turn_clause_to_interim_repr(clause: Clause, suffix: str = "_x"):
    head_vars = dict(
        [(v, ind) for ind, v in enumerate(clause.get_head().get_variables())]
    )

    return [
        tuple([a.get_predicate()]
              + [
                  head_vars[t] if isinstance(t, Variable) and t in head_vars else t
                  for t in a.get_terms()
              ])
        for a in clause.get_literals()
    ]


def construct_recursive_rule(rules: Sequence[Clause]):
    base_cases = [x for x in rules if not x.is_recursive()]
    recursive_rules = [x for x in rules if x.is_recursive()]
    head_predicate = rules[0].get_head().get_predicate()

    # turn each clause into its body: [(predicate, arg1, arg2, ...)]
    base_cases = [_turn_clause_to_interim_repr(x) for x in base_cases]

    recursive_rules = [_turn_clause_to_interim_repr(x) for x in recursive_rules]

    # variables that need to be created in the generic function
    bc_vars = [set(reduce(lambda x, y: x + y, [[v for v in c if isinstance(v, Variable)] for c in x], [])) for x in base_cases]
    rc_vars = [set(reduce(lambda x, y: x + y, [[v for v in c if isinstance(v, Variable)] for c in x], [])) for x in recursive_rules]

    def generic_recusive_predicate(
            *args,
            head=head_predicate,
            bases=base_cases,
            recursion=recursive_rules,
            bvars=bc_vars,
            rvars=rc_vars
    ):
        bvars = [
            dict(
                [(c, kanren.var()) for c in v]
                + [(x, args[x]) for x in range(head.get_arity())]
            )
            for v in bvars
        ]
        rvars = [
            dict(
                [(c, kanren.var()) for c in v]
                + [(x, args[x]) for x in range(head.get_arity())]
            )
            for v in rvars
        ]

        base_cases = [
            [
                a[0].as_kanren()(
                    *[
                        bvars[ind][ar] if ar in bvars[ind] else ar.get_name()
                        for ar in a[1:]
                    ]
                )
                for a in cl
            ]
            for ind, cl in enumerate(bases)
        ]

        recursion = [
            [
                a[0].as_kanren()(
                    *[
                        rvars[ind][ar] if ar in rvars[ind] else ar.get_name()
                        for ar in a[1:]
                    ]
                )
                if a[0] != head_predicate
                else kanren.core.Zzz(
                    generic_recusive_predicate,
                    *[
                        rvars[ind][ar] if ar in rvars[ind] else ar.get_name()
                        for ar in a[1:]
                    ]
                )
                for a in cl
            ]
            for ind, cl in enumerate(recursion)
        ]

        all_for_conde = base_cases + recursion

        return kanren.conde(*all_for_conde)

    return generic_recusive_predicate
