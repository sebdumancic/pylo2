from abc import ABC
from dataclasses import dataclass
from functools import reduce
from typing import Dict, Tuple, Sequence, Set, Union

import kanren
import z3

# from loreleai.language import MUZ, KANREN_LOGPY

MUZ = "muz"
LP = 1
FOL = 2
KANREN_LOGPY = "logpy"


class Type:
    def __init__(self, name: str):
        self.name = name
        self.elements = set()
        self._engine_objects = {}

    def add(self, elem):
        self.elements.add(elem)

    def remove(self, elem):
        self.elements.remove(elem)

    def add_engine_object(self, elem):
        if z3.is_sort(elem):
            self._engine_objects[MUZ] = elem
        else:
            raise Exception(f"unknown Type object {type(elem)}")

    def get_engine_obj(self, eng):
        assert eng in [MUZ, KANREN_LOGPY]
        return self._engine_objects[eng]

    def as_muz(self):
        return self._engine_objects[MUZ]

    def as_kanren(self):
        raise Exception("types not supported in kanren")

    def __add__(self, other):
        self.add(other)

    def __repr__(self):
        return self.name

    def __len__(self):
        return len(self.elements)

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(self.__repr__())


class Term:
    """
        Term base class. A common base class for Predicate, Constant, Variable and Functor symbols.
    """

    def __init__(self, name, sym_type: Type = None):
        self.name = name
        if sym_type is None:
            self.type = c_type("thing")
        else:
            self.type = sym_type
        self.hash_cache = None
        self._engine_objects = {}

    def arity(self) -> int:
        """
        Returns the arity of the term

        Returns:
             int
        """
        raise Exception("Not implemented!")

    def get_type(self) -> "Type":
        """
        Returns the type of the term
        """
        return self.type

    def get_name(self) -> str:
        """
        Returns the name of the term

        Return:
            [str]
        """
        return self.name

    def add_engine_object(self, elem) -> None:
        """
        Adds an engine object representing the

        """
        raise NotImplementedError()

    def as_muz(self):
        """
        Returns the object's representation in Z3 Datalog engine (muZ)
        """
        return self._engine_objects[MUZ]

    def as_kanren(self):
        """
        Returns the object's representation in the miniKanren engine
        """
        return self._engine_objects[KANREN_LOGPY]

    def get_engine_obj(self, eng):
        assert eng in [MUZ, KANREN_LOGPY]
        return self._engine_objects[eng]

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return self.name == other.name and self.type == other.type
        else:
            return False

    def __repr__(self):
        return self.name

    def __hash__(self):
        if self.hash_cache is None:
            self.hash_cache = hash(self.__repr__())
        return self.hash_cache  # hash(self.__repr__())


@dataclass
class Constant(Term):
    """
    Implements a constant in
    """

    def __init__(self, name, sym_type):
        assert (name[0].islower() or name[0] in ["'", '"']), f"Constants should be name with lowercase {name}"
        super().__init__(name, sym_type)
        self._id = len(sym_type)
        self.type.add(self)

    def arity(self) -> int:
        return 1

    def id(self) -> int:
        return self._id

    def add_engine_object(self, elem):
        if z3.is_bv_value(elem):
            self._engine_objects[MUZ] = elem
        elif isinstance(elem, str):
            self._engine_objects[KANREN_LOGPY] = elem
        else:
            raise Exception(f"unsupported Constant object {type(elem)}")

    def __repr__(self):
        return self.name

    def __hash__(self):
        if self.hash_cache is None:
            self.hash_cache = hash(self.__repr__())
        return self.hash_cache  # hash(self.__repr__())


@dataclass
class Variable(Term):
    """
    Implements a Variable functionality
    """

    def __init__(self, name: str, sym_type: Type = None):
        assert name[0].isupper(), f"Variables should be name uppercase {name}"
        if sym_type is None:
            sym_type = c_type("thing")
        if name[0].islower():
            raise Exception("Variables should uppercase!")
        super().__init__(name, sym_type)

    def arity(self):
        return 1

    def add_engine_object(self, elem):
        if z3.is_expr(elem):
            self._engine_objects[MUZ] = elem
        elif isinstance(elem, kanren.Var):
            self._engine_objects[KANREN_LOGPY] = elem
        else:
            raise Exception(f"unsupported Variable object: {type(elem)}")

    def __repr__(self):
        return self.name

    def __hash__(self):
        if self.hash_cache is None:
            self.hash_cache = hash(self.__repr__() + "/" + str(self.type))
        return self.hash_cache  # hash(self.__repr__() + "/" + str(self.type))

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return self.name == other.name and self.type == other.type
        else:
            return False


class Functor:
    def __init__(self, name: str, arity: int, types: Sequence[Type] = None):
        self._name: str = name
        self._arity: int = arity
        self._arg_types: Sequence[Type] = types

    def get_name(self) -> str:
        return self._name

    def get_arity(self) -> int:
        return self._arity

    def __eq__(self, other):
        if isinstance(other, Functor):
            return self._name == other._name and self._arity == other._arity
        else:
            return False

    def __hash__(self):
        return hash(f"func:{self._name}/{self._arity}")

    def __repr__(self):
        return self._name

    def __call__(
            self, *args: Union[str, "Constant", "Variable", "Structure", "List", "Pair", int, float]
    ) -> "Structure":
        args_to_use = []
        global global_context
        elem: Union[str, "Constant", "Variable", "Structure", "List", "Pair", int, float]
        for ind, elem in enumerate(args):
            if isinstance(elem, str) and (elem[0].islower() or elem[0] in {"'", '"'}):
                if self._arg_types is None:
                    args_to_use.append(c_const(elem))
                else:
                    args_to_use.append(c_const(elem, self._arg_types[ind]))
            elif isinstance(elem, str) and elem[0].isupper():
                if self._arg_types is None:
                    args_to_use.append(c_var(elem))
                else:
                    args_to_use.append(c_var(elem, self._arg_types[ind]))
            elif isinstance(elem, (Constant, Variable, Structure, List, Pair, int, float)):
                args_to_use.append(elem)
            else:
                raise Exception(
                    f"don't know how to convert {type(elem)} {elem} to term"
                )

        return Structure(self, args_to_use)


@dataclass
class Structure(Term):
    def __init__(self, functor: "Functor", arguments: Sequence[Term]):
        super(Structure, self).__init__(functor.get_name())
        self.arguments: Sequence[Term] = arguments
        self._functor: Functor = functor

    def __repr__(self):
        return "{}({})".format(self.name, ",".join([str(x) for x in self.arguments]))

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return (
                    self.name == other.name
                    and len(self.arguments) == len(other.arguments)
                    and all([x == y for (x, y) in zip(self.arguments, other.arguments)])
            )
        else:
            return False

    def arity(self):
        return len(self.arguments)

    def get_functor(self) -> Functor:
        return self._functor

    def get_arguments(self) -> Sequence[Term]:
        return [x for x in self.arguments]

    def add_engine_object(self, elem):
        if isinstance(elem, tuple):
            # add object as (engine name, object)
            assert elem[0] in [MUZ, KANREN_LOGPY]
            self._engine_objects[elem[0]] = elem[1]
        elif z3.is_func_decl(elem):
            self._engine_objects[MUZ] = elem
        elif isinstance(elem, kanren.Relation):
            self._engine_objects[KANREN_LOGPY] = elem
        else:
            raise Exception(f"unsupported Predicate object {type(elem)}")

    def get_engine_obj(self, eng):
        assert eng in [MUZ, KANREN_LOGPY]
        return self._engine_objects[eng]


list_func = Functor(".", 2)

# Swipl uses '[|]' as the functor for lists
# GNU PRolog uses '.' as the list functor
# XSB uses '.' as the list functor

# list conventions
#    -  [...] is a list in which empty list as the last element is implicitly assumed
#    -  if the user wants a something list [a|Y] (no empty list at the end), it has to explicitly construct it with pairs


class List(Structure):
    def __init__(self, elements: Sequence[Union[Term, int, float, str]]):
        argsToUse = []
        for elem in elements:
            if isinstance(elem, str) and elem[0].isupper() and elem[0] not in {'"', "'"}:
                argsToUse.append(global_context.variable(elem))
            elif isinstance(elem, str) and (elem[0].islower() or elem[0] in {'"', "'"}):
                argsToUse.append(global_context.constant(elem))
            elif isinstance(elem, (Constant, Variable, Structure, Predicate, List)):
                argsToUse.append(elem)
            elif isinstance(elem, (int, float)):
                argsToUse.append(elem)
            else:
                raise Exception(
                    f"Predicate:Don't know how to convert {type(elem)} {elem} to term"
                )
        super(List, self).__init__(list_func, argsToUse)

    def __repr__(self):
        return f"[{','.join([str(x) for x in self.arguments])}]"


pair_functor = Functor("[|]", 2)


class Pair(Structure):

    def __init__(self, left: Union[Term, int, float, str], right: Union[Term, int, float, str]):
        if isinstance(left, (Term, Constant, Variable, Structure, 'List', int, float)):
            self._left = left
        elif isinstance(left, str) and (left[0].islower() or left[0] in {"'", '"'}):
            self._left = global_context.constant(left)
        elif isinstance(left, str) and left[0].isupper():
            self._left = global_context.variable(left)
        else:
            raise Exception(f" don't know how to convert {left}")

        if isinstance(right, (Term, Constant, Variable, Structure, 'List', int, float)):
            self._right = right
        elif isinstance(right, str) and (right[0].islower() or right[0] in {"'", '"'}):
            self._right = global_context.constant(right)
        elif isinstance(right, str) and right[0].isupper():
            self._right = global_context.variable(right)
        else:
            raise Exception(f" don't know how to convert {right}")

        super(Pair, self).__init__(pair_functor, [self._left, self._right])

    def __repr__(self):
        return f"[{self._left} | {self._right}]"

    def get_left(self):
        return self._left

    def get_right(self):
        return self._right



@dataclass
class Predicate:
    def __init__(self, name: str, arity: int, arguments: Sequence[Type] = None):
        self.name = name
        self.arity = arity
        self.argument_types = (
            arguments if arguments else [Type("thing") for _ in range(arity)]
        )
        self.hash_cache = None
        self._engine_objects = {}

    def get_name(self) -> str:
        return self.name

    def get_arity(self) -> int:
        return self.arity

    def get_arg_types(self) -> Sequence[Type]:
        return self.argument_types

    def signature(self) -> Tuple[str, int]:
        return self.name, self.get_arity()

    def as_proposition(self) -> "Atom":
        return Atom(self, [])

    def add_engine_object(self, elem):
        if isinstance(elem, tuple):
            # add object as (engine name, object)
            assert elem[0] in [MUZ, KANREN_LOGPY]
            self._engine_objects[elem[0]] = elem[1]
        elif z3.is_func_decl(elem):
            self._engine_objects[MUZ] = elem
        elif isinstance(elem, kanren.Relation):
            self._engine_objects[KANREN_LOGPY] = elem
        else:
            raise Exception(f"unsupported Predicate object {type(elem)}")

    def get_engine_obj(self, eng):
        assert eng in [MUZ, KANREN_LOGPY]
        return self._engine_objects[eng]

    def as_muz(self):
        return self._engine_objects[MUZ]

    def as_kanren(self):
        return self._engine_objects[KANREN_LOGPY]

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return (
                    self.get_name() == other.get_name()
                    and self.get_arity() == other.get_arity()
                    and all(
                [
                    x == y
                    for (x, y) in zip(self.argument_types, other.get_arg_types())
                ]
            )
            )
        else:
            return False

    def __repr__(self):
        # return "{}({})".format(
        #     self.name, ",".join([str(x) for x in self.argument_types])
        # )
        return self.name

    def __hash__(self):
        if self.hash_cache is None:
            self.hash_cache = hash(self.__repr__())
        return self.hash_cache

    def _map_to_object(
            self, name: str, arg_position: int
    ) -> Union[Constant, Variable, Structure]:
        if "(" in name:
            raise Exception("automatically converting to structure not yet supported")
        elif name[0].islower() or name[0] in {'"', "'"}:
            return c_const(name, self.argument_types[arg_position])
        elif name[0].isupper():
            return c_var(name, self.argument_types[arg_position])
        else:
            raise Exception(f"don't know how to parse {name} to object")

    def __call__(self, *args, **kwargs):
        assert len(args) == self.get_arity()
        assert all([isinstance(x, (Constant, Variable, Structure, List, Pair, str, int, float)) for x in args])
        global global_context

        args = [
            x
            if isinstance(x, (Constant, Variable, Structure, List, Pair, int, float))
            else self._map_to_object(x, ind)
            for ind, x in enumerate(args)
        ]

        return Atom(self, list(args))


class Literal(ABC):
    def __init__(self):
        self._properties: Dict = {}
        self._hash_cache: int = None

    def add_property(self, property_name: str, value):
        self._properties[property_name] = value

    def get_property(self, property_name: str):
        return self._properties.get(property_name, None)

    def substitute(self, term_map: Dict[Term, Term]):
        raise NotImplementedError

    def get_predicate(self) -> Predicate:
        raise NotImplementedError

    def get_variables(self) -> Sequence[Variable]:
        raise NotImplementedError

    def get_terms(self) -> Sequence[Term]:
        raise NotImplementedError


@dataclass
class Atom(Literal):
    def __init__(
            self, predicate: Predicate, arguments: Sequence[Union[Term, int, float]]
    ):
        super(Atom, self).__init__()
        self.predicate = predicate
        self.arguments = arguments
        self.arg_signature = []

    def substitute(self, term_map: Dict[Term, Term]):
        return c_literal(
            self.predicate,
            [term_map[x] if x in term_map else x for x in self.arguments],
        )

    def get_predicate(self) -> Predicate:
        return self.predicate

    def get_predicates(self) -> Set[Predicate]:
        return {self.get_predicate()}

    def get_variables(self) -> Sequence[Variable]:
        return [x for x in self.arguments if isinstance(x, Variable)]

    def get_terms(self) -> Sequence[Term]:
        return [x for x in self.arguments]

    def get_arguments(self) -> Sequence[Term]:
        return [x for x in self.arguments]

    def as_muz(self):
        args = [x.as_muz() for x in self.arguments]
        return self.predicate.as_muz()(*args)

    def as_kanren(self, base_case_recursion=None):
        # not used here, provides base cases for the recursion
        args = [x.as_kanren() for x in self.arguments]
        return self.predicate.as_kanren()(*args)

    def __repr__(self):
        if self.predicate.get_arity() > 0:
            return f"{self.predicate}({','.join([str(x) for x in self.arguments])})"
        else:
            return f"{self.predicate}"

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return (
                    self.predicate == other.predicate and self.arguments == other.arguments
            )
        else:
            return False

    def __and__(self, other) -> "Body":
        return Body(self, other)

    def __le__(self, other: Union["Atom", "Not", "Body"]) -> "Clause":
        if isinstance(other, Body):
            return Clause(self, other)
        else:
            return Clause(self, [other])

    def __hash__(self):
        if self._hash_cache is None:
            self._hash_cache = hash(self.__repr__())

        return self._hash_cache


@dataclass
class Not(Literal):
    def __init__(self, formula: Atom):
        super(Not, self).__init__()
        self.atom: Atom = formula

    def substitute(self, term_map: Dict[Term, Term]) -> "Not":
        return Not(self.atom.substitute(term_map))

    def get_variables(self) -> Sequence[Variable]:
        return self.atom.get_variables()

    def get_terms(self) -> Sequence[Term]:
        return self.atom.get_terms()

    def get_atom(self) -> Atom:
        return self.atom

    def get_predicate(self) -> Predicate:
        return self.atom.get_predicate()

    def as_muz(self):
        return z3.Not(self.atom.as_muz())

    def as_kanren(self, base_case_recursion=None):
        raise Exception("miniKanren does not support negation")

    def __repr__(self):
        return f"\\+ {str(self.atom)}"

    def __hash__(self):
        if self._hash_cache is None:
            self._hash_cache = hash(self.__repr__())

        return self._hash_cache


@dataclass
class Body:
    def __init__(self, *literals):
        self._literals: Sequence[Union[Atom, Not]] = list(literals)
        self._hash_cache = None

    def get_literals(self) -> Sequence[Union[Atom, Not]]:
        return self._literals

    def get_predicates(self) -> Set[Predicate]:
        return {x.get_predicate() for x in self._literals}

    def get_variables(self) -> Sequence[Variable]:
        """
        Returns the variables of the literals in the body
        """
        vars_ordered = []
        vars_covered = set()
        for i in range(len(self._literals)):
            to_add = [
                x for x in self._literals[i].get_variables() if x not in vars_covered
            ]
            vars_ordered += to_add
            vars_covered = vars_covered.union(to_add)

        return vars_ordered

    def substitute(self, term_map: Dict[Term, Term]):
        return Body(*[x.substitute(term_map) for x in self._literals])

    def substitute_predicate(self, old_predicate: Predicate, new_predicate: Predicate):
        return Body(
            *[
                x
                if x.get_predicate() != old_predicate
                else new_predicate(*x.get_arguments())
                for x in self._literals
            ]
        )

    def __and__(self, other) -> "Body":
        if isinstance(other, Literal):
            self._literals += [other]
            return self
        elif isinstance(other, Predicate):
            self._literals += [other.as_proposition()]
            return self
        elif isinstance(other, Body):
            self._literals += other.get_literals()
            return self
        else:
            raise Exception(
                f"Body can be constructed only with Atom or Body, not {type(other)}"
            )

    def __add__(self, other):
        if isinstance(other, Literal):
            literals = self._literals + [other]
            return Body(*literals)
        elif isinstance(other, Predicate):
            literals = self._literals + [other.as_proposition()]
            return Body(*literals)
        elif isinstance(other, Body):
            literals = self._literals + other.get_literals()
            return Body(*literals)
        else:
            raise Exception(
                f"Body can be constructed only with Atom or Body, not {type(other)}"
            )

    def __repr__(self):
        return f":- {', '.join([str(x) for x in self._literals])}"

    def __len__(self):
        return len(self._literals)

    def __hash__(self):
        if self._hash_cache is None:
            self._hash_cache = hash(self.__repr__())

        return self._hash_cache

    def __eq__(self, other):
        if isinstance(other, Body) and len(self._literals) == len(other):
            return all([x == y for x, y in zip(self._literals, other.get_literals())])
        else:
            return False


@dataclass
class Clause:
    """
    Implements the clause functionality

    Args:
        head (Atom): head atom of the clause
        body (List(Atom)): list of atoms in the body of the clause
    """

    def __init__(
            self,
            head: Union[Atom, Predicate],
            body: Union[Sequence[Union[Atom, Not]], Body],
    ):
        super(Clause, self).__init__()
        if isinstance(head, Predicate):
            self._head: Atom = head.as_proposition()
        else:
            self._head: Atom = head

        if isinstance(body, Body):
            self._body: Body = body
        else:
            self._body: Body = Body(*body)
        # self._body = self._get_atom_order()
        self._terms = set()
        self._repr_cache = None
        self.term_signatures = None
        self.inverted_term_signatures = None
        self._hash_cache = None

        for lit in self._body.get_literals():
            self._terms = self._terms.union(lit.get_terms())

    def substitute(self, term_map: Dict[Term, Term]):
        """
            Substitute the terms in the clause

            Args:
                term_map (Dict[Term, Term]): mapping of the terms to their replacements
                                             (key: term from the clause, value: new term to replace it with)

            Return:
                new clause with the replaced literals
        """
        return Clause(self._head.substitute(term_map), self._body.substitute(term_map),)

    def substitute_head_predicate(self, new_pred: Predicate):
        """
        Replaces the current head predicate with the new one
        """
        assert new_pred.get_arity() == self._head.get_predicate().get_arity()
        return Clause(new_pred(*self._head.get_arguments()), self._body)

    def substitute_predicate(self, old_predicate: Predicate, new_predicate: Predicate):
        """
        substitute every occurrence of old_predicate with new_predicate

        """
        new_head = (
            self._head
            if self._head.get_predicate() != old_predicate
            else new_predicate(*self._head.get_arguments())
        )

        new_body = self._body.substitute_predicate(old_predicate, new_predicate)

        return Clause(new_head, new_body)

    def get_body(self) -> Body:
        return self._body

    def get_predicates(self) -> Set[Predicate]:
        """
            Returns the predicates in the clause
        """
        return self._body.get_predicates()

    def get_variables(self) -> Sequence[Variable]:
        """
            Returns the of variables in the clause
        """
        variables = self.get_head_variables()
        variables += [x for x in self.get_body_variables() if x not in variables]
        return variables

    def get_head_variables(self) -> Sequence[Variable]:
        """
            Returns only the head variables
        """
        return self._head.get_variables()

    def get_body_variables(self) -> Sequence[Variable]:
        """
            Returns variables appearing in the body
        """
        vars_ordered = []
        vars_covered = set()
        body_lits = self._body.get_literals()
        for i in range(len(body_lits)):
            to_add = [x for x in body_lits[i].get_variables() if x not in vars_covered]
            vars_ordered += to_add
            vars_covered = vars_covered.union(to_add)

        return vars_ordered

    def get_literals(self, with_predicates: Set[Predicate] = None) -> Sequence[Literal]:
        """
            Returns the set of atoms in the clause

            Args:
                with_predicates (Set[Predicates], optional): return only atoms with these predicates
        """
        if with_predicates is None:
            return self._body.get_literals()
        else:
            return [
                x
                for x in self._body.get_literals()
                if x.get_predicate() in with_predicates
            ]

    def get_head(self):
        return self._head

    def get_term_signatures(self):
        if self.term_signatures is None:
            self.term_signatures = _create_term_signatures(self._body.get_literals())
            self.inverted_term_signatures = dict(
                [(frozenset(v.items()), k) for k, v in self.term_signatures.items()]
            )

        return self.term_signatures

    def has_singleton_var(self) -> bool:
        var_count = {}
        for v in self._head.get_variables():
            if v not in var_count:
                var_count[v] = 0
            var_count[v] += 1

        for atm in self._body.get_literals():
            for v in atm.get_variables():
                if v not in var_count:
                    var_count[v] = 0
                var_count[v] += 1

        return len([1 for k, v in var_count.items() if v == 1]) > 0

    def substitute_atoms(
            self,
            atoms_to_replace: Sequence[Union[Atom, Not]],
            new_atom: Atom,
            substitutes: Dict[Term, Term],
    ) -> "Clause":
        """
        Substitutes some atoms in the body with a new atoms

        Args:
            atoms_to_replace (list[Atom]): atom to replace in the clause
            new_atom (Atom): atom to use as the replacement
            substitutes (Dict[Term, Term]): terms substitutes to use in the new atom
        """
        return Clause(
            self._head,
            [new_atom.substitute(substitutes)]
            + [x for x in self._body.get_literals() if x not in atoms_to_replace],
            )

    def is_recursive(self) -> bool:
        """
        Returns true if the clause is recursive
        """
        return self._head.get_predicate() in self._body.get_predicates()

    def as_muz(self):
        return self._head.as_muz(), [x.as_muz() for x in self._body.get_literals()]

    def as_kanren(self, base_case_recursion=None):
        if self.is_recursive():
            raise Exception(
                f"recursive rules should not be constructed with .as_kanren() method but should use 'construct_recursive' from kanren package"
            )
        # Should associate a conj goal with the predicate in the head
        # has to be a function
        # rename all variables to make sure there are no strange effects

        # head vars need to be bound to input args of the function
        head_vars = dict([(x, ind) for ind, x in enumerate(self._head.get_variables())])

        # all other arguments need to be bound to their kanren constructs
        other_args = [x.get_terms() for x in self._body.get_literals()]
        other_args = set(reduce(lambda x, y: x + y, other_args, []))
        # remove head variables; these should be bounded to the function arguments
        other_args = [x for x in other_args if x not in head_vars]

        def generic_predicate(*args, core_obj=self, hvars=head_vars, ovars=other_args):
            vars_to_use = dict([(v, kanren.var()) for v in ovars])
            return kanren.conde(
                [
                    x.get_predicate().as_kanren()(
                        *[
                            args[hvars[y]] if y in hvars else vars_to_use[y]
                            for y in x.get_terms()
                        ]
                    )
                    for x in core_obj.get_literals()
                ]
            )

        return generic_predicate

    def __contains__(self, item):
        if isinstance(item, Predicate):
            return item.get_name() in self._body.get_predicates()
        elif isinstance(item, Atom):
            return (
                    len(
                        [
                            x
                            for x in self._body.get_literals()
                            if x.get_predicate().get_name()
                               == item.get_predicate().get_name()
                        ]
                    )
                    > 0
            )
        else:
            return False

    def __add__(self, other: Union[Atom, Not]):
        return Clause(self._head, self._body + [other])

    def __len__(self):
        return len(self._body)

    def __and__(self, other: Atom):
        self._body += [other]
        # self._body = self._get_atom_order()
        return self

    # def _get_atom_order(self):
    #     head_vars = self._head.get_variables()
    #     all_atoms = [x for x in self._body]
    #     focus_vars = [head_vars[0]]
    #     processed_vars = set()
    #     atom_order = []
    #
    #     while len(all_atoms) > 0:
    #         matching_atms = [
    #             x
    #             for x in all_atoms
    #             if any([y in focus_vars for y in x.get_variables()])
    #         ]
    #         matching_atms = sorted(
    #             matching_atms,
    #             key=lambda x: min(
    #                 [
    #                     x.get_variables().index(y) if y in x.get_variables() else 5
    #                     for y in focus_vars
    #                 ]
    #             ),
    #         )
    #         processed_vars = processed_vars.union(focus_vars)
    #         atom_order += matching_atms
    #         all_atoms = [x for x in all_atoms if x not in matching_atms]
    #         focus_vars = reduce(
    #             (lambda x, y: x + y),
    #             [x.get_variables() for x in matching_atms if x not in processed_vars]
    #         )
    #
    #     return atom_order

    def __repr__(self):
        if self._repr_cache is None:
            if len(self._body):
                self._repr_cache = "{} :- {}".format(
                    self._head, ",".join([str(x) for x in self._body.get_literals()])
                )
            else:
                self._repr_cache = f"{self._head}"
        return self._repr_cache

    def __hash__(self):
        if self._hash_cache is None:
            var_map = {}
            for var in self._head.get_variables():
                if var not in var_map:
                    var_map[var] = len(var_map)

            for atm in self._body.get_literals():
                for v in atm.get_variables():
                    if v not in var_map:
                        var_map[v] = len(var_map)

            head_rep = f"{self._head.get_predicate().get_name()}({','.join([str(var_map[x] for x in self._head.get_variables())])})"
            bodies = [
                f"{x.get_predicate().get_name()}({','.join([str(var_map[t]) if t in var_map else str(t) for t in x.get_terms()])})"
                for x in self._body.get_literals()
            ]
            bodies = ",".join(bodies)

            self._hash_cache = hash(f"{head_rep} :- {bodies}")

        return self._hash_cache  # hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, Clause) and len(self) == len(other):
            return True if self._head == other.get_head() and self._body == other.get_body() else False
        else:
            return False


@dataclass
class Procedure:
    def __init__(self, clauses: Sequence[Clause]):
        self._clauses = clauses

    def get_clauses(self) -> Sequence[Clause]:
        return self._clauses

    def substitute_head_predicate(self, new_pred: Predicate) -> "Procedure":
        new_clauses = []

        for ind in range(len(self._clauses)):
            if isinstance(self._clauses[ind], Disjunction):
                new_clauses.append(
                    self._clauses[ind].substitute_head_predicate(new_pred)
                )
            else:
                new_clauses.append(
                    self._clauses[ind].substitute_predicate(
                        self._clauses[ind].get_head().get_predicate(), new_pred
                    )
                )

        if isinstance(self, Disjunction):
            return Disjunction(new_clauses)
        else:
            return Recursion(new_clauses)

    def substitute_predicate(self, old_predicate: Predicate, new_predicate: Predicate):
        new_clauses = []

        for ind in range(len(self._clauses)):
            new_clauses.append(
                self._clauses[ind].substitute_predicate(old_predicate, new_predicate)
            )

        if isinstance(self, Disjunction):
            return Disjunction(new_clauses)
        else:
            return Recursion(new_clauses)


class Disjunction(Procedure):
    def __init__(self, clauses: Sequence[Clause]):
        super().__init__(clauses)


class Recursion(Procedure):
    def __init__(self, clauses: Sequence[Clause]):
        super().__init__(clauses)

    def get_base_case(self) -> Sequence[Clause]:
        return [x for x in self._clauses if not x.is_recursive()]

    def get_recursive_case(self) -> Sequence[Clause]:
        return [x for x in self._clauses if x.is_recursive()]


class Program:
    def __init__(self, clauses: Sequence[Union[Clause, Procedure, Atom]]):
        self._clauses: Sequence[Union[Clause, Procedure, Atom]] = clauses

    def get_clauses(
            self, predicates: Set[Predicate] = None
    ) -> Sequence[Union[Clause, Procedure, Atom]]:
        if predicates:
            return [x for x in self._clauses if any([p for p in x.get_predicates()])]
        else:
            return self._clauses

    def __len__(self):
        return len(self.get_clauses())

    def num_literals(self) -> int:
        return sum([len(x) for x in self._clauses])

    def get_predicates(self) -> Set[Predicate]:
        raise Exception("Not implemented yet!")


class Context:
    def __init__(self):
        self._predicates = {}  # name/arity -> Predicate
        self._variables = {}  # domain -> {name -> Variable}
        self._constants = {}  # domain -> {name -> Constant}
        self._literals = {}  # Predicate -> { tuple of terms -> Atom}
        self._domains = {"thing": Type("thing"), "number": Type("number")}  # name -> Type
        self._id_to_constant = {}  # domain (str) -> {id -> Constant}
        self._functors = {2: {}}  # arity -> name -> Functor

        self._functors[2]["."] = list_func

    def _predicate_sig(self, name, arity):
        return f"{name}/{arity}"

    def get_predicates(self) -> Sequence[Predicate]:
        return [v for k, v in self._predicates.items()]

    def get_constants(self) -> Sequence[Constant]:
        p = [[v for k, v in self._constants[z].items()] for z in self._constants]
        return reduce(lambda x, y: x + y, p, [])

    def get_variables(self) -> Sequence[Variable]:
        return reduce(
            lambda x, y: x + y,
            [[v for k, v in self._variables[z].items()] for z in self._variables],
            [],
        )

    def get_types(self) -> Sequence[Type]:
        return [v for k, v in self._domains.items()]

    def constant_by_id(self, c_id: int, c_type: Union[str, Type]) -> Constant:
        if isinstance(c_type, Type):
            c_type = c_type.name

        return self._id_to_constant[c_type][c_id]

    def type(self, name):
        if name not in self._domains:
            t = Type(name)
            self._domains[name] = t

        return self._domains[name]

    def predicate(self, name, arity, domains=()) -> Predicate:
        if len(domains) == 0:
            domains = [self._domains["thing"]] * arity

        domains = [d if isinstance(d, Type) else self.type(d) for d in domains]

        if not self._predicate_sig(name, arity) is self._predicates:
            p = Predicate(name, arity, domains)
            self._predicates[self._predicate_sig(name, arity)] = p

        return self._predicates[self._predicate_sig(name, arity)]

    def variable(self, name, domain=None) -> Variable:
        if domain is None:
            domain = "thing"
        elif isinstance(domain, Type):
            domain = domain.name

        if domain not in self._variables:
            self._variables[domain] = {}

        if name not in self._variables[domain]:
            v = Variable(name, sym_type=self._domains[domain])
            self._variables[domain][name] = v

        return self._variables[domain][name]

    def fresh_variable(self, domain=None) -> Variable:
        if domain is None:
            domain = "thing"

        v_id = 1
        while True:
            if f"_V{v_id}" not in self._variables[domain]:
                break
            else:
                v_id += 1

        return self.variable(f"_V{v_id}", domain)

    def constant(self, name, domain=None) -> Constant:
        if domain is None:
            domain = "thing"
        elif isinstance(domain, Type):
            domain = domain.name

        if domain not in self._id_to_constant:
            self._id_to_constant[domain] = {}

        if domain not in self._constants:
            self._constants[domain] = {}

        if name not in self._constants[domain]:
            c = Constant(name, self._domains[domain])
            self._constants[domain][name] = c
            self._id_to_constant[domain][c.id()] = c

        return self._constants[domain][name]

    def literal(self, predicate: Predicate, arguments: Sequence[Term]) -> "Atom":
        if predicate not in self._literals:
            self._literals[predicate] = {}

        if tuple(arguments) not in self._literals[predicate]:
            self._literals[predicate][tuple(arguments)] = Atom(predicate, arguments)

        return self._literals[predicate][tuple(arguments)]

    def find_domain(self, const: Union[str, Constant]):
        """
            Find domain of a constant
        :param const:
        :return:
        """
        if isinstance(const, Constant):
            const = const.get_name()

        for dom in self._constants:
            if const in self._constants[dom]:
                return self.type(dom)
        else:
            return self.type("thing")

    def functor(self, name: str, arity: int = None, types: Sequence[Type] = None):
        # check if already exists
        found = []
        for ar in (
                [arity]
                if (arity is not None and arity in self._functors)
                else self._functors
        ):
            if name in self._functors[ar]:
                found.append(self._functors[ar][name])
        if len(found) == 1:
            return found[0]
        else:
            # if doesn't exist
            assert (
                arity is not None or types is not None,
                "creating new functor requires either arity or argument types",
            )
            if types is None:
                if arity not in self._functors:
                    self._functors[arity] = {}
                self._functors[arity][name] = Functor(name, arity)
                return self._functors[arity][name]
            else:
                arity = len(types)
                if arity not in self._functors:
                    self._functors[arity] = {}
                self._functors[arity][name] = Functor(name, arity, types)
                return self._functors[arity][name]

    def symbol(self, name: str, arity: int = None, types: Sequence[Type] = None):
        for dom in self._constants:
            if name in self._constants[dom]:
                return self._constants[dom][name]
        for ar in self._functors:
            if name in self._functors[ar]:
                return self._functors[ar][name]
        for ar in self._predicates:
            if f"{name}/{ar}" in self._predicates:
                return self._predicates[f"{name}/{ar}"]

        assert arity is not None
        # if symbol does not exists, assume predicate
        return self.functor(name, arity, types)


global_context = Context()


def _get_proper_context(ctx) -> Context:
    if ctx is None:
        global global_context
        return global_context
    else:
        return ctx


def c_pred(name, arity, domains=(), ctx: Context = None) -> Predicate:
    ctx = _get_proper_context(ctx)
    return ctx.predicate(name, arity, domains=domains)


def c_const(name, domain=None, ctx: Context = None) -> Constant:
    ctx = _get_proper_context(ctx)
    return ctx.constant(name, domain=domain)


def c_id_to_const(id: int, type: Union[str, Type], ctx: Context = None) -> Constant:
    ctx = _get_proper_context(ctx)
    return ctx.constant_by_id(id, type)


def c_var(name, domain=None, ctx: Context = None) -> Variable:
    ctx = _get_proper_context(ctx)
    return ctx.variable(name, domain=domain)


def c_literal(
        predicate: Predicate, arguments: Sequence[Term], ctx: Context = None
) -> Atom:
    ctx = _get_proper_context(ctx)
    return ctx.literal(predicate, arguments)


def c_fresh_var(domain=None, ctx: Context = None) -> Variable:
    ctx = _get_proper_context(ctx)
    return ctx.fresh_variable(domain=domain)


def c_find_domain(const: Union[str, Constant], ctx: Context = None) -> Type:
    ctx = _get_proper_context(ctx)
    return ctx.find_domain(const)


def c_type(name: str, ctx: Context = None) -> Type:
    ctx = _get_proper_context(ctx)
    return ctx.type(name)


def c_functor(
        name: str, arity: int = None, types: Sequence[Type] = None, ctx: Context = None
) -> Functor:
    ctx = _get_proper_context(ctx)
    return ctx.functor(name, arity, types)


def c_symbol(
        name: str, arity: int = None, types: Sequence[Type] = None, ctx: Context = None
) -> Union[Term, Functor, Predicate]:
    ctx = _get_proper_context(ctx)
    return ctx.symbol(name, arity, types)


def _are_two_set_of_literals_identical(
        clause1: Union[Sequence[Atom], Dict[Sequence[Predicate], Dict]],
        clause2: Union[Sequence[Atom], Dict[Sequence[Predicate], Dict]],
) -> bool:
    """
    Checks whether two sets of literal are identical, i.e. unify, up to the variable naming
    :param clause1:
    :param clause2:
    :return:
    """
    clause1_sig = (
        _create_term_signatures(clause1) if isinstance(clause1, list) else clause1
    )
    clause2_sig = (
        _create_term_signatures(clause2) if isinstance(clause2, list) else clause2
    )

    if len(clause1_sig) != len(clause2_sig):
        return False
    else:
        clause1_sig = dict([(frozenset(v.items()), k) for k, v in clause1_sig.items()])
        clause2_sig = dict([(frozenset(v.items()), k) for k, v in clause2_sig.items()])

        matches = clause1_sig.keys() & clause2_sig.keys()

        # TODO: this is wrong if constants are used
        # terms_cl1 = set()
        # for l in clause1:
        #     for v in l.get_terms():
        #         terms_cl1.add(v)
        #
        # terms_cl2 = set()
        # for l in clause2:
        #     for v in l.get_terms():
        #         terms_cl2.add(v)

        return len(matches) == max(len(clause1_sig), len(clause2_sig))


def _create_term_signatures(
        literals: Sequence[Union[Atom, Not]]
) -> Dict[Term, Dict[Tuple[Predicate], int]]:
    """
        Creates a term signature for each term in the set of literals

        A term signature is a list of all appearances of the term in the clause.
        The appearances are described as a tuple (predicate name, position of the term in the arguments)

        Args:
            literals (List[Atom]): list of literals of the clause

        Returns:
            returns a dictionary with the tuples as keys and their corresponding number of occurrences in the clause

    """
    term_signatures = {}

    for lit in literals:
        for ind, trm in enumerate(lit.get_terms()):
            if trm not in term_signatures:
                term_signatures[trm] = {}

            if isinstance(lit, Not):
                tmp_atm = lit.get_atom()
                if isinstance(tmp_atm, Atom):
                    tmp_sig = (f"not_{tmp_atm.get_predicate().get_name()}", ind)
                else:
                    raise Exception("Only atom can be negated!")
            else:
                tmp_sig = (lit.get_predicate().get_name(), ind)
            term_signatures[trm][tmp_sig] = term_signatures[trm].get(tmp_sig, 0) + 1

    return term_signatures
