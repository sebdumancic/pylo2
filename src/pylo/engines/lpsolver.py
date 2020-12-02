from abc import ABC, abstractmethod
from typing import Union

from ..language.commons import Atom, Clause, Context, global_context
from ..language.lp import Predicate, Type, Constant, Variable, Not


class LPSolver(ABC):
    """
    An abstract class implementing a logic programming solver/reasoner

    Arguments:
        name [str]: name of the engine
        knowledge_base (default: None): facts to use
                                        Not supported yet
        background_knowledge (default: None): background knowledge (clauses)
                                              Not supported yet
        ctx [Context] (default: global context): context to use

    """

    def __init__(self, name, knowledge_base=None, background_knowledge=None, ctx: Context = None):
        self._name = name
        self._knowledge = knowledge_base
        self._background = background_knowledge
        #self._solver = None
        if ctx is None:
            ctx = global_context
        self._create_objects(ctx)

    def _create_objects(self, ctx: Context):
        """
        Translates the objects from the context to engine-specific objects

        Arguments:
            ctx [Context]: context to use
        """
        [self.declare_type(t) for t in ctx.get_types()]
        [self.declare_constant(c) for c in ctx.get_constants()]
        [self.declare_predicate(p) for p in ctx.get_predicates()]
        [self.declare_variable(v) for v in ctx.get_variables()]

    def get_name(self) -> str:
        """
        Returns the name of an engine
        """
        return self._name

    @abstractmethod
    def declare_type(self, elem_type: Type) -> None:
        """
        Instantiates the type/domain/sort within the solver.
        Needs to make sure that the reference is provided to the original Type object

        Arguments:
            elem_type [Type]: type to instantiate
        """
        raise NotImplementedError()

    @abstractmethod
    def declare_predicate(self, elem_predicate: Predicate) -> None:
        """
        Instantiates the predicate symbol within the solver.
        Needs to make sure that the reference is provided to the original Predicate object

        Arguments:
            elem_predicate [Predicate]: predicate to instantiate
        """
        raise NotImplementedError()

    @abstractmethod
    def declare_constant(self, elem_constant: Constant) -> None:
        """
        Instantiates the constant symbol within the solver.
        Needs to make sure that the reference is provided to the original Constant object

        Arguments:
            elem_constant [Constant]: constant to instantiate
        """
        raise NotImplementedError()

    @abstractmethod
    def declare_variable(self, elem_variable: Variable) -> None:
        """
        Instantiates the variable symbol within the solver.
        Needs to make sure that the reference is provided to the original Variable object

        Arguments:
            elem_variable [Variable]: variable to instantiate
        """
        raise NotImplementedError()

    @abstractmethod
    def assert_fact(self, fact: Atom) -> None:
        """
        Asserts fact to the solvers knowledge base

        Arguments:
            fact [Literal]: fact to assert
        """
        raise NotImplementedError()

    @abstractmethod
    def assert_rule(self, rule: Clause) -> None:
        """
        Asserts rule to the solvers knowledge base

        Arguments:
             rule [Clause]: rule to assert
        """
        raise NotImplementedError()

    @abstractmethod
    def has_solution(self, *query: Union[Atom, Not]):
        """
                Checks whether the query can be satisfied by the knowledge base

                Arguments:
                    query (Union[Atom,Clause]): list of literals

                Return:
                    True/False
                """
        raise NotImplementedError()

    @abstractmethod
    def query(self, *query, **kwargs):
        """
                Checks whether the query can be satisfied by the knowledge base

                Arguments:
                    query (Union[Atom,Clause]): list of literals

                Return:
                    True/False
                """
        raise NotImplementedError()

