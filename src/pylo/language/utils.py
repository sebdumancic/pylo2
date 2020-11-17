from typing import Union, Sequence, Dict

import networkx as nx

from .commons import Predicate, Constant, Atom, Variable, c_fresh_var


# MUZ = "muz"
# LP = 1
# FOL = 2
# KANREN_LOGPY = "logpy"


def triplet(subject: Union[str, Constant, Variable],
            relation: Predicate,
            object: Union[str, Constant, Variable]) -> Atom:
    """
    Allows to specify a literal as a triplet

    Arguments:
        subject: name of the subject/head entity; '?' means variable
        relation: the relation between the entities
        object: name of th object/tail entity; '?' means variable

    Return:
        a literal
    """
    assert relation.get_arity() == 2
    arg_types = relation.get_arg_types()
    return relation(c_fresh_var(arg_types[0]) if isinstance(subject, str) and subject == "?" else subject,
                    c_fresh_var(arg_types[1]) if isinstance(object, str) and object == "?" else object)


def nx_to_loreleai(graph: nx.Graph, relation_map: Dict[str, Predicate] = None) -> Sequence[Atom]:
    """
    Converts a NetworkX graph into Loreleai representation

    To indicate the type of relations and nodes, the functions looks for a 'type' attribute

    Arguments:
        graph: NetworkX graph
        relation_map: maps from edge types to predicates
    """

    literals = []

    if relation_map is None:
        relation_map = {}

    for (u, v, t) in graph.edges.data('type', default=None):
        literals.append(relation_map[t](u, v))

    return literals


