from abc import ABC
from typing import Sequence, Union
import typing


class InputError(Exception):
    pass


class Term(ABC):

    def __init__(self, name: str):
        self._name: str = name

    def get_name(self) -> str:
        return self._name

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._name == other._name
        else:
            return False

    def __hash__(self):
        return hash(f"{type(self)}:{self._name}")

    def __repr__(self):
        return self._name


def is_float(value: str):
    try:
        float(value)
        return True
    except ValueError:
        return False


def starts_with_digit(name: str):
    return name[0].isdigit()


def starts_with_lower_case(name: str):
    return name[0].islower()


def is_surrounded_by_single_quotes(name: str):
    quote_char = "'"
    return len(name) > 3 and name[0] == quote_char and name[-1] == quote_char and quote_char not in name[1:-1]


def is_valid_constant(name: str):
    if len(name) == 0:
        return False

    return (starts_with_digit(name)
            or starts_with_lower_case(name)
            or is_float(name)
            or is_surrounded_by_single_quotes(name)
            )


class Constant(Term):

    def __init__(self, name: str):
        if len(name) == 0:
            raise InputError('empty Constant')
        assert is_valid_constant(name), f"Constants should be name with lowercase {name}"
        super().__init__(name)


class Variable(Term):

    def __init__(self, name: str):
        if len(name) == 0:
            raise InputError("empty variable")

        assert name[0].isupper() or name[0] == "_", f"Variables should be name uppercase {name}"
        super().__init__(name)


class Functor:

    def __init__(self, name: str, arity: int):
        self._name: str = name
        self._arity: int = arity

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

    def __call__(self, *args: Union[str, "Constant", "Variable", "Structure", "List", int, float]) -> "Structure":
        args_to_use = []
        global global_context
        elem: Union[str, "Constant", "Variable", "Structure", "List", int, float]
        for elem in args:
            # STARTS with lower case
            if isinstance(elem, str) and elem.islower():
                args_to_use.append(global_context.get_constant(elem))
            # STARTS with uppercase
            elif isinstance(elem, str) and elem.isupper():
                args_to_use.append(global_context.get_variable(elem))
            # Is a Constant, Variable, Structure, List, int or Float
            elif isinstance(elem, (Constant, Variable, Structure, List, int, float)):
                args_to_use.append(elem)
            else:
                raise Exception(f"don't know how to convert {type(elem)} {elem} to term")

        return Structure(self, args_to_use)


class Structure(Term):

    def __init__(self, functor: "Functor", args: Sequence[Union[Term, int, float]]):
        self._functor: Functor = functor
        self._args: Sequence[Union[Term, int, float]] = args
        super().__init__(name=functor.get_name())

    def get_functor(self) -> Functor:
        return self._functor

    def get_arguments(self) -> Sequence[Union[Term, int, float]]:
        return self._args

    def __eq__(self, other):
        if isinstance(other, Structure):
            if self._functor != other._functor or len(self._args) != len(other._args):
                return False
            else:
                return all([x == y for x, y in zip(self._args, other._args)])
        else:
            return False

    def __repr__(self):
        return f"{self._name}({','.join([str(x) for x in self._args])})"

    def __hash__(self):
        return hash(str(self))


list_func = Functor(".", 2)

# Swipl uses '[|]' as the functor for lists
# GNU PRolog uses '.' as the list functor
# XSB uses '.' as the list functor

# list conventions
#    -  [...] is a list in which empty list as the last element is implicitly assumed
#    -  if the user wants a something list [a|Y] (no empty list at the end), it has to explicitly construct it with pairs


class List(Structure):

    def __init__(self, elements: Sequence[Union[Term, int, float]]):
        argsToUse = []
        for elem in elements:
            if isinstance(elem, str) and elem[0].isupper():
                argsToUse.append(global_context.get_variable(elem))
            elif isinstance(elem, str) and elem[0].islower():
                argsToUse.append(global_context.get_constant(elem))
            elif isinstance(elem, (Constant, Variable, Structure, Predicate, List)):
                argsToUse.append(elem)
            elif isinstance(elem, (int, float)):
                argsToUse.append(elem)
            else:
                raise Exception(f"Predicate:Don't know how to convert {type(elem)} {elem} to term")
        super(List, self).__init__(list_func, argsToUse)

    def __repr__(self):
        return f"[{','.join([str(x) for x in self._args])}]"


class Predicate:

    def __init__(self, name: str, arity: int):
        self._name: str = name
        self._arity: int = arity

    def get_name(self) -> str:
        return self._name

    def get_arity(self) -> int:
        return self._arity

    def as_proposition(self) -> "Atom":
        return Atom(self, [])

    def __eq__(self, other):
        if isinstance(other, Predicate):
            return self._name == other._name and self._arity == other._arity
        else:
            return False

    def __hash__(self):
        return hash(f"pred:{self._name}/{self._arity}")

    def __repr__(self):
        return self._name

    def __call__(self, *args: Union[str, "Constant", "Variable", "Structure", "Predicate", int, float]) -> "Atom":
        argsToUse = []
        # global global_context
        elem: Union[str, "Constant", "Variable", "Structure", "Predicate", int, float]
        for elem in args:
            if isinstance(elem, str) and elem.isdigit():
                if '.' in elem:
                    argsToUse.append(float(elem))
                else:
                    argsToUse.append(int(elem))
            if isinstance(elem, str) and elem[0].isupper():
                argsToUse.append(global_context.get_variable(elem))
            elif isinstance(elem, str) and elem[0].islower():
                argsToUse.append(global_context.get_constant(elem))
            elif isinstance(elem, (Constant, Variable, Structure, Predicate)):
                argsToUse.append(elem)
            elif isinstance(elem, (int, float)):
                argsToUse.append(elem)
            else:
                raise Exception(f"Predicate:Don't know how to convert {type(elem)} {elem} to term")

        return Atom(self, argsToUse)


class Literal:

    def get_predicate(self) -> Predicate:
        raise Exception("not implemented yet!")

    def get_arguments(self) -> Sequence[Union[Term, int, float]]:
        raise Exception("not implemented yet!")

    def is_ground(self) -> bool:
        raise Exception("not implemented yet!")


class Atom(Literal):

    def __init__(self, predicate: Predicate, args: Sequence[Union[Term, int, float]]):
        self._predicate = predicate
        self._args: Sequence[Union[Term, int, float]] = args

    def get_predicate(self) -> Predicate:
        return self._predicate

    def get_arguments(self) -> Sequence[Union[Term, int, float]]:
        return self._args

    def is_ground(self) -> bool:
        return not any([isinstance(x, Variable) for x in self._args])

    def __and__(self, other: Union["Atom", "Negation"]) -> "Conj":
        return Conj(self, other)

    def __le__(self, other: Union["Atom", "Negation", "Conj"]) -> "Clause":
        if isinstance(other, (Atom, Negation)):
            return Clause(self, Conj(other))
        else:
            return Clause(self, other)

    def __eq__(self, other) -> bool:
        if isinstance(other, Atom):
            return self._predicate == other._predicate and \
                   len(self._args) == len(other._args) and \
                   all([x == y for x, y in zip(self._args, other._args)])
        else:
            return False

    def __repr__(self):
        if self._predicate.get_arity() > 0:
            return f"{self._predicate}({','.join([str(x) for x in self._args])})"
        else:
            return f"{self._predicate}"

    def __hash__(self):
        return hash(str(self))


class Negation(Literal):

    def __init__(self, literal: Atom):
        self._lit: Atom = literal

    def get_literal(self) -> "Atom":
        return self._lit

    def get_predicate(self) -> Predicate:
        return self._lit.get_predicate()

    def get_arguments(self) -> Sequence[Union[Term, int, float]]:
        return self._lit.get_arguments()

    def is_ground(self) -> bool:
        return self._lit.is_ground()

    def __and__(self, other: Union["Atom", "Negation"]) -> "Conj":
        return Conj(self, other)

    def __eq__(self, other):
        if isinstance(other, Negation):
            return self._lit == other._lit
        else:
            return False

    def __repr__(self):
        return f"\\+ {self._lit}"


class Conj:

    def __init__(self, *lits: Union["Atom", "Negation"]):
        self._lits: typing.List[Union["Atom", "Negation"]] = list(lits)

    def get_literals(self) -> typing.List[Union["Atom", "Negation"]]:
        return self._lits

    def __repr__(self):
        return ",".join([str(x) for x in self._lits])

    def __eq__(self, other) -> bool:
        if isinstance(other, Conj):
            return all([x == y for x, y in zip(self._lits, other._lits)])
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __and__(self, other: Union["Atom", "Negation", "Conj"]) -> "Conj":
        if isinstance(other, (Atom, Negation)):
            self._lits += [other]
        elif isinstance(other, Predicate):
            self._lits += [other.as_proposition()]
        elif isinstance(other, Conj):
            self._lits += other.get_literals()
        else:
            raise Exception(f"Don't know how to add object of type {type(other)} to Conj")
        return self


class Clause:

    def __init__(self, head: Union[Atom, Predicate], body: Conj):
        if isinstance(head, Predicate):
            self._head = head.as_proposition()
        else:
            self._head: Atom = head
        self._body: Conj = body

    def get_head(self) -> Atom:
        return self._head

    def get_body(self) -> Conj:
        return self._body

    def __and__(self, other: Union["Atom", "Negation", "Conj"]):
        if isinstance(other, (Atom, Negation)):
            self._body & other
        elif isinstance(other, Conj):
            self._body = Conj(self._body.get_literals() + other.get_literals())
        else:
            raise Exception(f"Don't know how to add bject of type {type(other)} to Clause")

    def __repr__(self):
        return f"{self._head} :- {self._body}"


class Context:

    def __init__(self):
        self._consts = {}
        self._vars = {}
        self._predicates = {}
        self._functors = {}

    def get_constant(self, name: str):
        if name not in self._consts:
            self._consts[name] = Constant(name)

        return self._consts[name]

    def get_variable(self, name: str):
        if name not in self._vars:
            self._vars[name] = Variable(name)

        return self._vars[name]

    def get_fresh_variable(self, save=False):
        name = [chr(x) for x in range(ord('A'), ord('Z') + 1) if chr(x) not in self._vars][0]
        if len(name) == 0:
            name = [f"{chr(x)}{chr(y)}" for x in range(ord('A'), ord('Z') + 1) for y in range(ord('A'), ord('Z') + 1) if
                    chr(x) not in self._vars][0]
        var = Variable(name)

        if save:
            self._vars[name] = var

        return var

    def get_functor(self, name: str, arity: int):
        if name not in self._functors:
            self._functors[name] = {}

        if arity not in self._functors[name]:
            self._functors[name][arity] = Functor(name, arity)

        return self._functors[name][arity]

    def get_predicate(self, name: str, arity: int):
        if name not in self._predicates:
            self._predicates[name] = {}

        if arity not in self._predicates[name]:
            self._predicates[name][arity] = Predicate(name, arity)

        return self._predicates[name][arity]

    def get_symbol(self, name, **kwargs):
        if name in self._consts:
            return self._consts[name]
        elif name in self._functors:
            if 'arity' in kwargs:
                return self._functors[name][kwargs['arity']]
            else:
                ks = list(self._functors[name].keys())
                if len(ks) > 1:
                    raise Exception(f"Cannot uniquely identify functor symbol {name}")
                return self._functors[name][ks[0]]
        elif name in self._predicates:
            if 'arity' in kwargs:
                return self._predicates[name][kwargs['arity']]
            else:
                ks = list(self._predicates[name].keys())
                if len(ks) > 1:
                    raise Exception(f"Cannot uniquely identify predicate symbol {name}")
                return self._predicates[name][ks[0]]
        else:
            raise Exception(f"Cannot identify symbol {name}")


global_context = Context()
