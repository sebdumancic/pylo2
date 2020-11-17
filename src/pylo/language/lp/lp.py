from __future__ import annotations

from functools import reduce
from typing import List, Dict, Set, Tuple, Sequence

import pygraphviz as pgv

# from . import parse
from ..commons import Predicate, Program, c_var, \
    c_pred, c_const, c_literal, Clause, _are_two_set_of_literals_identical


class ClausalTheory(Program):

    def __init__(self, clauses: Sequence[Clause] = None, read_from_file: str = None):
        assert clauses is not None or read_from_file is not None

        if read_from_file:
            # TODO: fix this for clauses that spread on more than one line
            clauses = []
            inf = open(read_from_file)

            for line in inf.readlines():
                if len(line) > 3 and not line.startswith('#') and not line.startswith('%') and not line.startswith('//') and not line.startswith('true.'):
                    clauses.append(parse(line.strip().replace('.', '')))

        super(ClausalTheory, self).__init__(clauses)

    def get_clauses(self, predicates: Set[Predicate] = None) -> Sequence[Clause]:
        if predicates:
            return [x for x in self._formulas if any([p in predicates for p in x.get_predicates()])]
        else:
            return self._formulas

    def remove_formulas_with_predicates(self, predicates_in_questions: Set[Predicate]):
        """
        Removes all formulas that use at least one of the provided predicates
        """
        self._formulas = [x for x in self._formulas if not any([p in predicates_in_questions for p in x.get_predicates()])]

    def get_predicates(self) -> Set[Predicate]:
        return reduce((lambda x, y: x.union(y)), [x.get_predicates().union({x.get_head().get_predicate()}) for x in self._formulas])

    def remove_duplicates(self):
        new_forms = []

        frms_per_length = {}
        for frm in self._formulas:
            l = len(frm)
            if l not in frms_per_length:
                frms_per_length[l] = []
            frms_per_length[l].append(frm)

        indices_to_remove = {}
        for l in frms_per_length:
            indices_to_remove[l] = set()
            for ind in range(0, len(frms_per_length[l])-1):
                for ind_i in range(ind+1, len(frms_per_length[l])):
                    cl1 = frms_per_length[l][ind]
                    cl2 = frms_per_length[l][ind_i]

                    if cl1.get_predicates() == cl2.get_predicates() \
                            and _are_two_set_of_literals_identical(cl1.get_term_signatures(), cl2.get_term_signatures()):
                        indices_to_remove[l].add(ind_i)

        for l in frms_per_length:
            removed = 0
            for ind in indices_to_remove[l]:
                frms_per_length[l].pop(ind - removed)
                removed += 1
            new_forms += frms_per_length[l]

        self._formulas = new_forms

    def unfold(self):
        """
        Unfolds the theory

        A theory containing two clauses
                h :- d,c,r.
                d :- a,b.
        Would be unfolded into
                h :- a,b,c,r.

        Returns:
             unfolded theory [Theory]
        """

        def _unfold_recursively(clause: Clause, clause_index: Dict[Predicate, List[Clause]], forbidden_clauses: Set[
            Clause]) -> Tuple[List[Clause], Set[Clause]]:
            cl_predicates = [x.get_predicate() for x in clause.get_literals()]
            if len(forbidden_clauses) == 0:
                matching_clauses_for_unfolding = dict([(k, clause_index[k]) for k in cl_predicates if k in clause_index])
            else:
                matching_clauses_for_unfolding = dict([(k, [p for p in clause_index[k] if p not in forbidden_clauses]) for k in cl_predicates if k in clause_index])

            if len(matching_clauses_for_unfolding) == 0:
                return [clause], set()
            else:
                used_clauses = [v for k, v in matching_clauses_for_unfolding.items()]
                used_clauses = reduce(lambda x, y: x + y, used_clauses)
                _new_form = clause.unfold_with(used_clauses)
                # once the recursive clause is used, do not allow another usage again
                # recursive_clauses = set([x for x in used_clauses if x.is_recursive()])
                # used_clauses = [x for x in used_clauses if not x.is_recursive()]
                # NOT NEEDED ANYMORE BECAUSE RECURSIVE PREDICATES ARE REMOVED FROM THE CANDIDATE SET
                final = [_unfold_recursively(x, clause_index, forbidden_clauses) for x in _new_form]

                final_clauses = reduce(lambda x, y: x + y, [z[0] for z in final])
                final_exclusion = reduce(lambda x, y: x.union(y), [z[1] for z in final])

                return final_clauses, final_exclusion.union(used_clauses)

        # create clause index
        clause_index = {}
        new_set_of_formulas = []
        recursively_defined_predicates = set()

        for cl in self._formulas:
            if cl.is_recursive():
                # detect predicates with recursive definitions
                # do not use them for unfolding because they can remove finite traces
                recursively_defined_predicates.add(cl.get_head().get_predicate())

            head_pred = cl.get_head().get_predicate()
            if head_pred not in clause_index:
                clause_index[head_pred] = []
            clause_index[head_pred].append(cl)

        clauses_to_exclude = set()
        # excluding recursively defined predicates from the candidate set, so that they are not used
        clause_index = dict([(k, v) for k, v in clause_index.items() if k not in recursively_defined_predicates])

        for cl in self.get_clauses():
            if cl in clauses_to_exclude:
                continue

            cls, excls = _unfold_recursively(cl, clause_index, set()) # at the beginning, no forbidden clause (used for recursive ones)
            new_set_of_formulas += cls
            clauses_to_exclude = clauses_to_exclude.union(excls)

        return ClausalTheory(new_set_of_formulas)

    def visualize(self, filename: str, only_numbers=False):
        predicates_in_bodies_only = set()  # names are the predicate names
        predicates_in_heads = set() # names are clauses

        for cl in self._formulas:
            predicates_in_heads.add(cl.get_head().get_predicate())
            predicates_in_bodies_only = predicates_in_bodies_only.union([x.get_predicate() for x in cl.get_literals()])

        predicates_in_bodies_only = [x for x in predicates_in_bodies_only if x not in predicates_in_heads]

        graph = pgv.AGraph(directed=True)
        cl_to_node_name = {}

        for p in predicates_in_bodies_only:
            cl_to_node_name[p] = len(cl_to_node_name) if only_numbers else f"{p.get_name()}/{p.get_arity()}"
            graph.add_node(cl_to_node_name[p], color='blue')

        for cl in self._formulas:
            if cl.get_head().get_predicate() not in cl_to_node_name:
                ind = len(cl_to_node_name)
                #cl_to_node_name[cl] = ind if only_numbers else str(cl)
                cl_to_node_name[cl.get_head().get_predicate()] = ind if only_numbers else str(cl.get_head().get_predicate())
                graph.add_node(cl_to_node_name[cl.get_head().get_predicate()], clause=cl.get_head().get_predicate(), color='black' if ('latent' in cl.get_head().get_predicate().get_name() or "_" in cl.get_head().get_predicate().get_name()) else 'red')

        for cl in self._formulas:
            body_p = [x.get_predicate() for x in cl.get_literals()]

            for p in body_p:
                graph.add_edge(cl_to_node_name[cl.get_head().get_predicate()], cl_to_node_name[p])

        graph.draw(filename, prog='dot')

    def __str__(self):
        return "\n".join([str(x) for x in self._formulas])

    def __len__(self):
        return len(self._formulas)

    def num_literals(self):
        return sum([len(x)+1 for x in self._formulas])


def _convert_to_atom(string: str):
    pred, args = string.strip().replace(')', '').split('(')
    args = args.split(',')

    pred = c_pred(pred, len(args))
    args = [c_const(x) if x.islower() else c_var(x) for x in args]

    return c_literal(pred, args)


def parse(string: str):
    if ":-" in string:
        head, body = string.split(":-")
        head, body = head.strip(), body.strip()
        body = [x + ")" for x in body.split("),")]
        head, body = _convert_to_atom(head), [_convert_to_atom(x) for x in body]
        return Clause(head, body)
    else:
        return _convert_to_atom(string)


