from abc import ABC, abstractmethod


class Prolog(ABC):

    @abstractmethod
    def __init__(self):
        self.is_released: bool = False

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def consult(self, filename: str):
        pass

    @abstractmethod
    def use_module(self, module: str, **kwargs):
        pass

    @abstractmethod
    def asserta(self, clause):
        pass

    @abstractmethod
    def assertz(self, clause):
        pass

    @abstractmethod
    def retract(selfself, clause):
        pass

    @abstractmethod
    def has_solution(self, query):
        pass

    @abstractmethod
    def query(self, *query, **kwargs):
        pass

    @abstractmethod
    def register_foreign(self, pyfunction, arity):
        pass




