from pylo.engines.prolog.prologsolver import (
    Prolog
)
from pylo.language.lp import Constant, Variable, Functor, Structure, List, Predicate, Atom, Not, Clause, \
    c_pred, c_const, c_var, c_functor, Pair
# from .prologsolver import Prolog
# from pylo.language.lp import Constant, Variable, Functor, Structure, Predicate, List, Atom, Not, Clause, \
#     list_func, Literal, c_pred, c_const, c_var, c_functor
import typing
import sys

sys.path.append("../../../build")

import swipy
from typing import Union, Dict, Sequence
from functools import reduce
import ctypes


def _const_to_swipy(const: Union[Constant, Predicate]):
    c = swipy.swipy_new_term_ref()
    swipy.swipy_put_atom_chars(c, const.get_name())
    return c


def _const_to_swipy_ref(const: Constant, swipy_ref):
    swipy.swipy_put_atom_chars(swipy_ref, const.get_name())


def _var_to_swipy(var: Variable, lit_var_store: Dict[Variable, int]):
    if var in lit_var_store:
        return lit_var_store[var]
    else:
        tmpV = swipy.swipy_new_term_ref()
        swipy.swipy_put_variable(tmpV)
        lit_var_store[var] = tmpV
        return tmpV


def _var_to_swipy_ref(var: Variable, swipy_ref, lit_var_store: Dict[Variable, int]):
    if var in lit_var_store:
        swipy.swipy_put_term(swipy_ref, lit_var_store[var])
    else:
        swipy.swipy_put_variable(swipy_ref)
        lit_var_store[var] = swipy_ref


def _num_to_swipy(num: Union[int, float]):
    n = swipy.swipy_new_term_ref()
    if isinstance(num, int):
        swipy.swipy_put_integer(n, num)
    else:
        swipy.swipy_put_float(n, num)

    return n


def _num_to_swipy_ref(num: Union[int, float], swipy_ref):
    if isinstance(num, int):
        swipy.swipy_put_integer(swipy_ref, num)
    else:
        swipy.swipy_put_float(swipy_ref, num)


def _functor_to_swipy(functor: Union[Functor, Predicate]):
    func_atm = swipy.swipy_new_atom(functor.get_name())
    func = swipy.swipy_new_functor(func_atm, functor.get_arity())
    return func


def _to_swipy(item, lit_var_store: Dict[Variable, int]):
    if isinstance(item, Constant):
        return _const_to_swipy(item)
    elif isinstance(item, Variable):
        return _var_to_swipy(item, lit_var_store)
    elif isinstance(item, (int, float)):
        return _num_to_swipy(item)
    elif isinstance(item, List):
        return _list_to_swipy(item, lit_var_store)
    elif isinstance(item, Pair):
        return _pair_to_swipy(item, lit_var_store)
    elif isinstance(item, Structure):
        return _structure_to_swipy(item, lit_var_store)
    else:
        raise Exception(f"don't know how to turn item {item} ({type(item)}) into swipy")


def _to_swipy_ref(item, swipy_ref, lit_var_store: Dict[Variable, int]):
    if isinstance(item, Constant):
        return _const_to_swipy_ref(item, swipy_ref)
    elif isinstance(item, Variable):
        return _var_to_swipy_ref(item, swipy_ref, lit_var_store)
    elif isinstance(item, (int, float)):
        return _num_to_swipy_ref(item, swipy_ref)
    elif isinstance(item, List):
        return _list_to_swipy_ref(item, swipy_ref, lit_var_store)
    elif isinstance(item, Pair):
        return _pair_to_swipy_ref(item, swipy_ref, lit_var_store)
    elif isinstance(item, Structure):
        return _structure_to_swipy_ref(item, swipy_ref, lit_var_store)
    else:
        raise Exception(f"don't know how to turn item {item} ({type(item)}) into swipy")


def _structure_to_swipy(item: Structure, lit_var_store: Dict[Variable, int]):
    func = _functor_to_swipy(item.get_functor())
    compound_arg = swipy.swipy_new_term_refs(item.get_functor().get_arity())
    struct_args = item.get_arguments()
    _to_swipy_ref(struct_args[0], compound_arg, lit_var_store)
    for i in range(1, item.get_functor().get_arity()):
        _to_swipy_ref(struct_args[i], compound_arg + i, lit_var_store)

    structure = swipy.swipy_new_term_ref()
    swipy.swipy_cons_functor(structure, func, compound_arg)

    return structure


def _structure_to_swipy_ref(item: Structure, swipy_ref, lit_var_store: Dict[Variable, int]):
    func = _functor_to_swipy(item.get_functor())
    compound_arg = swipy.swipy_new_term_refs(item.get_functor().get_arity())
    struct_args = item.get_arguments()
    _to_swipy_ref(struct_args[0], compound_arg, lit_var_store)
    for i in range(1, item.get_functor().get_arity()):
        _to_swipy_ref(struct_args[i], compound_arg + i, lit_var_store)

    swipy.swipy_cons_functor(swipy_ref, func, compound_arg)


def _list_to_swipy(item: List, lit_var_store: Dict[Variable, int]):
    list_term = swipy.swipy_new_term_ref()

    if len(item.get_arguments()) == 0:
        # if empty list
        swipy.swipy_put_nil(list_term)
    else:
        # if non-empty list
        clist_term = swipy.swipy_new_term_ref()

        swipy.swipy_put_nil(list_term)
        args = item.get_arguments()
        for ind in range(len(args) - 1, -1, -1):
            _to_swipy_ref(args[ind], clist_term, lit_var_store)
            swipy.swipy_cons_list(list_term, clist_term, list_term)

    return list_term


def _list_to_swipy_ref(item: List, swipy_ref, lit_var_store: Dict[Variable, int]):
    if len(item.get_arguments()) == 0:
        # if empty
        swipy.swipy_put_nil(swipy_ref)
    else:
        # if not empty
        clist_term = swipy.swipy_new_term_ref()

        swipy.swipy_put_nil(swipy_ref)
        args = item.get_arguments()
        for ind in range(len(args) - 1, -1, -1):
            _to_swipy_ref(args[ind], clist_term, lit_var_store)
            swipy.swipy_cons_list(swipy_ref, clist_term, swipy_ref)


def _pair_to_swipy(item: Pair, lit_var_store: Dict[Variable, int]):
    list_term = swipy.swipy_new_term_ref()
    head = swipy.swipy_new_term_ref()
    tail = swipy.swipy_new_term_ref()

    _to_swipy_ref(item.get_left(), head, lit_var_store)
    _to_swipy_ref(item.get_right(), tail, lit_var_store)

    swipy.swipy_cons_list(list_term, head, tail)

    return list_term


def _pair_to_swipy_ref(item: Pair, swipy_ref, lit_var_store: Dict[Variable, int]):
    head = swipy.swipy_new_term_ref()
    tail = swipy.swipy_new_term_ref()

    _to_swipy_ref(item.get_left(), head, lit_var_store)
    _to_swipy_ref(item.get_right(), tail, lit_var_store)

    swipy.swipy_cons_list(swipy_ref, head, tail)


def _lit_to_swipy(clause: Atom, lit_var_store: Dict[Variable, int]):
    if clause.get_predicate().get_arity() == 0:
        functor = _const_to_swipy(clause.get_predicate())
        return functor
    else:
        functor = _functor_to_swipy(clause.get_predicate())
        compound_arg = swipy.swipy_new_term_refs(clause.get_predicate().get_arity())
        args = clause.get_arguments()
        _to_swipy_ref(args[0], compound_arg, lit_var_store)
        for i in range(1, clause.get_predicate().get_arity()):
            _to_swipy_ref(args[i], compound_arg+i, lit_var_store)

        literal = swipy.swipy_new_term_ref()
        swipy.swipy_cons_functor(literal, functor, compound_arg)

        return literal


def _neg_to_swipy(clause: Not, lit_var_store: Dict[Variable, int]):
    lit = _lit_to_swipy(clause.get_atom(), lit_var_store)
    neg_atom = swipy.swipy_new_atom("\\+")
    neg_functor = swipy.swipy_new_functor(neg_atom, 1)

    entire_negation = swipy.swipy_new_term_ref()
    swipy.swipy_cons_functor(entire_negation, neg_functor, lit)

    return entire_negation


def _conjoin_literals(lits: Sequence[int]):
    if len(lits) == 1:
        return lits[0]
    else:
        f_atm = swipy.swipy_new_atom(",")
        conj_functor = swipy.swipy_new_functor(f_atm, 2)

        compound_arg = swipy.swipy_new_term_refs(2)
        conj = swipy.swipy_new_term_ref()
        swipy.swipy_put_term(compound_arg, lits[0])
        swipy.swipy_put_term(compound_arg + 1, _conjoin_literals(lits[1:]))
        swipy.swipy_cons_functor(conj, conj_functor, compound_arg)

        return conj


def _cl_to_swipy(clause: Clause, lit_var_store: Dict[Variable, int]):
    body: typing.Sequence[Union[Atom, Not]] = clause.get_body().get_literals()
    head: Atom = clause.get_head()

    body: typing.List[int] = [_lit_to_swipy(x, lit_var_store)
                              if isinstance(x, Atom)
                              else _neg_to_swipy(x, lit_var_store)
                              for x in body]

    head = _lit_to_swipy(head, lit_var_store)
    body = _conjoin_literals(body)

    clause_atom = swipy.swipy_new_atom(":-")
    clause_functor = swipy.swipy_new_functor(clause_atom, 2)

    entire_clause = swipy.swipy_new_term_ref()
    compound_arg = swipy.swipy_new_term_refs(2)
    swipy.swipy_put_term(compound_arg, head)
    swipy.swipy_put_term(compound_arg + 1, body)
    swipy.swipy_cons_functor(entire_clause, clause_functor, compound_arg)

    return entire_clause


def _swipy_to_const(term):
    name = swipy.swipy_get_atom_chars(term)
    return c_const(name if name[0].islower() else f"\"{name}\"")


def _swipy_to_int(term):
    return swipy.swipy_get_integer(term)


def _swipy_to_float(term):
    return swipy.swipy_get_float(term)


def _swipy_to_string(term):
    return c_const(swipy.swipy_get_string_chars(term))


def _swipy_to_var(term, swipy_term_to_var: Dict[int, Variable]):
    if term in swipy_term_to_var:
        return swipy_term_to_var[term]
    else:
        all_var_names = set([x.get_name() for x in swipy_term_to_var.values()])
        new_name = [chr(x) for x in range(ord('A'), ord('Z') + 1) if chr(x) not in all_var_names]
        if len(new_name) == 0:
            new_name = [f"{chr(x)}{chr(y)}" for x in range(ord('A'), ord('Z') + 1) for y in
                        range(ord('A'), ord('Z') + 1) if f"{chr(x)}{chr(y)}" not in all_var_names]
        new_name = new_name[0]
        new_var = Variable(new_name)
        swipy_term_to_var[term] = new_var
        return new_var


def _swipy_to_list(term):
    elements = []
    list = swipy.swipy_copy_term_ref(term)

    head = swipy.swipy_new_term_ref()

    while swipy.swipy_get_list(list, head, list):
        elements.append(_read_swipy(head))

    return List(elements)


def _swipy_to_pair(term):
    head = swipy.swipy_new_term_ref()
    tail = swipy.swipy_new_term_ref()

    swipy.swipy_get_head(term, head)
    swipy.swipy_get_tail(term, tail)

    return Pair(_read_swipy(head), _read_swipy(tail))


def _swipy_to_structure(term):
    name, arity = swipy.swipy_get_name_arity(term)
    name = swipy.swipy_atom_chars(name)
    functor = c_functor(name, arity)

    structure_elements = []
    for arg_ind in range(1, arity + 1):
        elem = swipy.swipy_new_term_ref()
        swipy.swipy_get_arg(arg_ind, term, elem)

        structure_elements.append(_read_swipy(elem))

    return functor(*structure_elements)


def _read_swipy(term, swipy_term_to_var={}):
    if swipy.swipy_is_atom(term):
        return _swipy_to_const(term)
    elif swipy.swipy_is_string(term):
        return _swipy_to_string(term)
    elif swipy.swipy_is_integer(term):
        return _swipy_to_int(term)
    elif swipy.swipy_is_float(term):
        return _swipy_to_float(term)
    elif swipy.swipy_is_list(term):
        return _swipy_to_list(term)
    elif swipy.swipy_is_pair(term):
        return _swipy_to_pair(term)
    elif swipy.swipy_is_compound(term):
        return _swipy_to_structure(term)
    elif swipy.swipy_is_variable(term):
        return _swipy_to_var(term, swipy_term_to_var)
    else:
        raise Exception(f"Unknown term type {swipy.swipy_term_type(term)}")


class SWIProlog(Prolog):

    def __init__(self, exec_path=None):
        if exec_path is None:
            exec_path = "/usr/local/bin/swipl"
        swipy.swipy_init(exec_path)
        self._callback_arities = {}
        self._wrapped_functions = {}
        self._wrap_refs_to_keep = []
        super(SWIProlog, self).__init__()

    def release(self):
        if not self.is_released:
            #swipy.swipy_cleanup(1)
            swipy.swipy_halt(1)
            self.is_released: bool = True

    def __del__(self):
        self.release()


    def consult(self, filename: str):
        string_term = swipy.swipy_new_term_ref()
        swipy.swipy_put_string_chars(string_term, filename)

        consult_pred = swipy.swipy_predicate("consult", 1, None)
        query = swipy.swipy_open_query(consult_pred, string_term)
        r = swipy.swipy_next_solution(query)
        swipy.swipy_close_query(query)

        if r == 0:
            raise Exception(f"something wrong when consulting file {filename}")

        return r

    def use_module(self, module_name: str, **kwargs):
        if module_name.startswith('library'):
            # create library functor
            library_term = swipy.swipy_new_atom("library")
            library_funct = swipy.swipy_new_functor(library_term, 1)

            # create inner module name: library([name])
            module_inner_name = module_name[:-1].replace('library(', '')
            inner_name = swipy.swipy_new_term_ref()
            swipy.swipy_put_atom_chars(inner_name, module_inner_name)

            # construct library(name)
            full_module = swipy.swipy_new_term_ref()
            swipy.swipy_cons_functor(full_module, library_funct, inner_name)
        else:
            full_module = swipy.swipy_new_term_ref()
            swipy.swipy_put_atom_chars(full_module, module_name)

        # load module
        use_module = swipy.swipy_predicate("use_module", 1, None)
        query = swipy.swipy_open_query(use_module, full_module)
        r = swipy.swipy_next_solution(query)
        swipy.swipy_close_query(query)

        if r == 0:
            raise Exception(f"could not load module {module_name}")

        return r

    def asserta(self, clause):
        var_store = {}
        if isinstance(clause, Atom):
            swipl_object = _lit_to_swipy(clause, var_store)
        else:
            swipl_object = _cl_to_swipy(clause, var_store)

        asserta = swipy.swipy_predicate("asserta", 1, None)
        query = swipy.swipy_open_query(asserta, swipl_object)
        r = swipy.swipy_next_solution(query)
        swipy.swipy_close_query(query)

        return r

    def assertz(self, clause: Union[Atom, Clause]):
        var_store = {}
        if isinstance(clause, Atom):
            swipl_object = _lit_to_swipy(clause, var_store)
        elif isinstance(clause, Clause):
            swipl_object = _cl_to_swipy(clause, var_store)
        else:
            raise Exception(f"can only assertz atoms or clauses (got {clause})")

        asserta = swipy.swipy_predicate("assertz", 1, None)
        query = swipy.swipy_open_query(asserta, swipl_object)
        r = swipy.swipy_next_solution(query)
        swipy.swipy_close_query(query)

        return r

    def retract(self, clause: Union[Atom, Clause]):
        if isinstance(clause, Atom):
            lit = _lit_to_swipy(clause, {})
        else:
            lit = _cl_to_swipy(clause, {})

        retract = swipy.swipy_predicate("retract", 1, None)
        query = swipy.swipy_open_query(retract, lit)
        r = swipy.swipy_next_solution(query)
        swipy.swipy_close_query(query)

        return r

    def has_solution(self, *query: Union[Atom, Not]):
        var_store = {}

        if len(query) == 1:
            query = query[0]
            predicate_name = query.get_predicate().get_name()
            query_args = swipy.swipy_new_term_refs(query.get_predicate().get_arity())

            for ind, arg in enumerate(query.get_arguments()):
                _to_swipy_ref(arg, query_args + ind, var_store)

            pred = swipy.swipy_predicate(predicate_name, query.get_predicate().get_arity(), None)
            query = swipy.swipy_open_query(pred, query_args)
            r = swipy.swipy_next_solution(query)
            swipy.swipy_close_query(query)

            return True if r else False
        else:
            swipy_objs = [_lit_to_swipy(x, var_store) if isinstance(x, Atom) else _neg_to_swipy(x, var_store) for x
                          in query]
            first = swipy_objs[0]
            rest = _conjoin_literals(swipy_objs[1:])

            compound_arg = swipy.swipy_new_term_refs(2)
            swipy.swipy_put_term(compound_arg, first)
            swipy.swipy_put_term(compound_arg + 1, rest)

            predicate = swipy.swipy_predicate(",", 2, None)
            query = swipy.swipy_open_query(predicate, compound_arg)
            r = swipy.swipy_next_solution(query)
            swipy.swipy_close_query(query)

            return True if r else False

    def _wrap_in_call_time(self, query, time):
        """
        Wraps the query in call_with_time_limit. Assumes that query is already translated to swipy
        :param query:
        :param time:
        :return:
        """
        func_atm = swipy.swipy_new_atom("call_with_time_limit")
        func = swipy.swipy_new_functor(func_atm, 2)

        compound_arg = swipy.swipy_new_term_refs(2)
        _num_to_swipy_ref(time, compound_arg)
        swipy.swipy_put_term(compound_arg + 1, query)

        final_term = swipy.swipy_new_term_ref()
        swipy.swipy_cons_functor(final_term, func, compound_arg)

        return final_term

    def _prepare_query(self, var_store, *query, max_time=None, max_depth=None, max_inference=None):
        """
        Prepares the query

        Return swipl-transformed predicate and arguments needed to posed the query to the engine

        :param var_store:
        :param query:
        :param max_time:
        :param max_depth:
        :param max_inference:
        :return:
        """
        if len(query) == 1:
            query = query[0]

            if not (max_time or max_depth or max_inference):
                predicate_name = query.get_predicate().get_name()
                query_args = swipy.swipy_new_term_refs(query.get_predicate().get_arity())

                for ind, arg in enumerate(query.get_arguments()):
                    _to_swipy_ref(arg, query_args + ind, var_store)

                pred = swipy.swipy_predicate(predicate_name, query.get_predicate().get_arity(), None)

                return pred, query_args
            else:
                query_term = _lit_to_swipy(query, var_store)

                if max_time:
                    # if time limit should be imposed on the query

                    pred = swipy.swipy_predicate("call_with_time_limit", 2, None)
                    query_args = swipy.swipy_new_term_refs(2)

                    swipy.swipy_put_integer(query_args, max_time)
                    swipy.swipy_put_term(query_args+1, query_term)

                    return pred, query_args
                elif max_depth or max_inference:
                    pred = swipy.swipy_predicate("call_with_depth_limit", 3, None) if max_depth else swipy.swipy_predicate("call_with_inference_limit", 3, None)
                    query_args = swipy.swipy_new_term_refs(3)
                    swipy.swipy_put_term(query_args, query_term)

                    if max_depth:
                        _num_to_swipy_ref(max_depth, query_args + 1)
                    else:
                        _num_to_swipy_ref(max_inference, query_args + 1)
                    swipy.swipy_put_variable(query_args + 2)

                    return pred, query_args

        else:
            swipy_objs = [_lit_to_swipy(x, var_store) if isinstance(x, Atom) else _neg_to_swipy(x, var_store) for x
                          in query]

            if not (max_time or max_depth or max_inference):
                first = swipy_objs[0]
                rest = _conjoin_literals(swipy_objs[1:])

                compound_arg = swipy.swipy_new_term_refs(2)
                swipy.swipy_put_term(compound_arg, first)
                swipy.swipy_put_term(compound_arg + 1, rest)

                predicate = swipy.swipy_predicate(",", 2, None)

                return predicate, compound_arg
            else:
                query_term = _conjoin_literals(swipy_objs)

                if max_time:
                    # if time limit should be imposed on the query
                    wrapped_term = self._wrap_in_call_time(query_term, max_time)
                    exception = swipy.swipy_new_atom('time_limit_exceeded')
                    fail = swipy.swipy_new_atom('fail')

                    pred = swipy.swipy_predicate("catch", 3, None)
                    query_args = swipy.swipy_new_term_refs(3)
                    swipy.swipy_put_term(query_args, wrapped_term)
                    swipy.swipy_put_term(query_args + 1, exception)
                    swipy.swipy_put_term(query_args + 2, fail)

                    return pred, query_args
                elif max_depth or max_inference:
                    pred = swipy.swipy_predicate("call_with_depth_limit", 3, None) if max_depth else swipy.swipy_predicate("call_with_inference_limit", 3, None)
                    query_args = swipy.swipy_new_term_refs(3)
                    swipy.swipy_put_term(query_args, query_term)

                    if max_depth:
                        _num_to_swipy_ref(max_depth, query_args + 1)
                    else:
                        _num_to_swipy_ref(max_inference, query_args + 1)
                    swipy.swipy_put_variable(query_args + 2)

                    return pred, query_args

    def query(self, *query, **kwargs):
        if 'max_solutions' in kwargs:
            max_solutions = kwargs['max_solutions']
        else:
            max_solutions = -1

        if 'time_limit' in kwargs:
            time_limit = kwargs['time_limit']
        else:
            time_limit = None

        if 'depth_limit' in kwargs:
            depth_limit = kwargs['depth_limit']
        else:
            depth_limit = None

        if 'inference_limit' in kwargs:
            inference_limit = kwargs['inference_limit']
        else:
            inference_limit = None

        vars_of_interest = [[y for y in x.get_arguments() if isinstance(y, Variable)] for x in query]
        vars_of_interest = reduce(lambda x, y: x + y, vars_of_interest, [])
        vars_of_interest = reduce(lambda x, y: x + [y] if y not in x else x, vars_of_interest, [])
        var_store = {}
        for v in vars_of_interest:
            tmp_v = swipy.swipy_new_term_ref()
            swipy.swipy_put_variable(tmp_v)
            var_store[v] = tmp_v

        # if len(query) == 1:
        #     query = query[0]
        #     predicate_name = query.get_predicate().get_name()
        #     query_args = swipy.swipy_new_term_refs(query.get_predicate().get_arity())
        #
        #     for ind, arg in enumerate(query.get_arguments()):
        #         _to_swipy_ref(arg, query_args + ind, var_store)
        #
        #     pred = swipy.swipy_predicate(predicate_name, query.get_predicate().get_arity(), None)
        #     query = swipy.swipy_open_query(pred, query_args)
        # else:
        #     swipy_objs = [_lit_to_swipy(x, var_store) if isinstance(x, Atom) else _neg_to_swipy(x, var_store) for x
        #                   in query]
        #     first = swipy_objs[0]
        #     rest = _conjoin_literals(swipy_objs[1:])
        #
        #     compound_arg = swipy.swipy_new_term_refs(2)
        #     swipy.swipy_put_term(compound_arg, first)
        #     swipy.swipy_put_term(compound_arg + 1, rest)
        #
        #     predicate = swipy.swipy_predicate(",", 2, None)
        #     query = swipy.swipy_open_query(predicate, compound_arg)

        pred, compound_arg = self._prepare_query(var_store, *query, max_time=time_limit, max_depth=inference_limit, max_inference=inference_limit)
        query = swipy.swipy_open_query(pred, compound_arg)

        r = swipy.swipy_next_solution(query)

        all_solutions = []
        var_index_var = dict([(var_store[v], v) for v in var_store])

        while r and max_solutions != 0:
            max_solutions -= 1

            tmp_solution = {}
            for var in var_store:
                tmp_solution[var] = _read_swipy(var_store[var], swipy_term_to_var=var_index_var)

            all_solutions.append(tmp_solution)
            r = swipy.swipy_next_solution(query)

        swipy.swipy_close_query(query)

        return all_solutions

    def _callback(self, arity):
        res = self._callback_arities.get(arity)
        if res is None:
            args = [ctypes.c_uint64] + [ctypes.c_uint64]*arity
            res = ctypes.CFUNCTYPE(*args)
            self._callback_arities[arity] = res

        return res

    def _foreign_wrapper(self, pyfunction):
        res = self._wrapped_functions.get(pyfunction)
        if res is None:
            def wrapper(*args):
                swipy_term_to_var = {}
                args = [_read_swipy(x, swipy_term_to_var) for x in args]
                print(f"function {pyfunction.__name__} with args: {args}")
                # TODO: pyfunction should take the original args as input in order to give the ability to put something in variables
                r = pyfunction(*args)
                return (r is None) and True or r

            res = wrapper
            self._wrapped_functions[pyfunction] = res

        return res

    def register_foreign(self, pyfunction, arity):
        cwrap = self._callback(arity)
        fwrap = self._foreign_wrapper(pyfunction)
        fwrap2 = cwrap(fwrap)
        self._wrap_refs_to_keep.append(fwrap2)

        res = swipy.swipy_register_foreign(pyfunction.__name__, arity, fwrap2, 0)

        return c_pred(pyfunction.__name__, arity)


if __name__ == '__main__':

    def test1():
        pl = SWIProlog()

        p = c_pred("p", 2)
        f = c_functor("t", 3)
        f1 = p("a", "b")

        pl.assertz(f1)

        X = c_var("X")
        Y = c_var("Y")

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

        member = c_pred("member", 2)

        query2 = member(X, l)

        rv = pl.query(query2)
        print("all solutions to list membership ", rv)

        r = c_pred("r", 2)
        f4 = r("a", l)
        f5 = r("a", "b")

        pl.asserta(f4)
        pl.asserta(f5)

        query3 = r(X, Y)

        rv = pl.query(query3)
        print("all solutions after adding list ", rv)

        # Foreign predicates

        def hello(t):
            print("Foreign: Hello", t)

        hello_pred = pl.register_foreign(hello, 1)
        # print(hello_pred)

        f_query = hello_pred("a")

        pl.has_solution(f_query)

        del pl

    def test2():
        pl = SWIProlog()

        bongard = c_pred('bongard', 2)
        circle = c_pred('circle', 2)
        inp = c_pred('in', 3)
        config = c_pred('pconfig', 3)
        triangle = c_pred('triangle', 2)
        square = c_pred('square', 2)

        pl.assertz(bongard(2, "la"))
        pl.assertz(circle(2, "o3"))
        pl.assertz(config(2, "o1", "up"))
        pl.assertz(config(2, "o2", "up"))
        pl.assertz(config(2, "o5", "up"))
        pl.assertz(triangle(2, "o1"))
        pl.assertz(triangle(2, "o2"))
        pl.assertz(triangle(2, "o5"))
        # pl.assertz(square(2, "o4"))
        pl.assertz(inp(2, "o4", "o5"))
        pl.assertz(inp(2, "o2", "o3"))

        A = c_var("A")
        B = c_var("B")
        C = c_var("C")
        D = c_var("D")

        #pl.assertz((bongard(A,"la") <= triangle(A,C) & inp(A, C, D)))

        res = pl.query(bongard(A, "la"), triangle(A,C), inp(A, C, D))

        print(res)

        del pl


    def test4():
        pl = SWIProlog()

        parent = c_pred("parent", 2)
        grandparent = c_pred("grandparent", 2)

        f1 = parent("p1", "p2")
        f2 = parent("p2", "p3")

        v1 = c_var("X")
        v2 = c_var("Y")
        v3 = c_var("Z")

        cl = (grandparent(v1, v3) <= parent(v1, v2) & parent(v2, v3))

        pl.assertz(f1)
        pl.assertz(f2)
        pl.assertz(cl)

        assert pl.has_solution(parent(v1, v2))
        assert not pl.has_solution(parent(v1, v1))
        assert len(pl.query(parent(v1, v2))) == 2
        assert len(pl.query(parent("p1", v1))) == 1
        assert pl.has_solution(parent("p1", "p2"))
        assert not pl.has_solution(parent("p2", "p1"))
        assert len(pl.query(parent("p1", v1), max_solutions=1)) == 1

        assert pl.has_solution(grandparent(v1, v2))
        assert pl.has_solution(grandparent("p1", v1))
        assert len(pl.query(grandparent("p1", v1), max_solutions=1)) == 1

        print(pl.query(grandparent(v1, v2)))

        pl.assertz(parent("p2", "p4"))
        pl.assertz(parent("p1", "p5"))
        print(pl.query(grandparent(v1, v2)))

        del pl

    def test5():
        solver = SWIProlog()

        edge = c_pred("edge", 2)
        path = c_pred("path", 2)

        f1 = edge("v1", "v2")
        f2 = edge("v1", "v3")
        f3 = edge("v2", "v4")

        X = c_var("X")
        Y = c_var("Y")
        Z = c_var("Z")

        cl1 = path(X, Y) <= edge(X, Y)
        cl2 = path(X, Y) <= edge(X, Z) & path(Z, Y)

        solver.assertz(f1)
        solver.assertz(f2)
        solver.assertz(f3)

        solver.assertz(cl1)
        solver.assertz(cl2)

        assert solver.has_solution(path("v1", "v2"))
        assert solver.has_solution(path("v1", "v4"))
        assert not solver.has_solution(path("v3", "v4"))

        assert len(solver.query(path("v1", X), max_solutions=1)[0]) == 1
        assert len(solver.query(path(X, "v4"), max_solutions=1)[0]) == 1
        assert len(solver.query(path(X, Y), max_solutions=1)[0]) == 2

        assert len(solver.query(path("v1", X))) == 3
        assert len(solver.query(path(X, Y))) == 4

        solver.assertz(edge("v4", "v5"))
        assert len(solver.query(path(X, Y))) == 7

        print(solver.query(edge(X, Y), edge(Y, Z), edge(Z,"W")))
        del solver

    def test6():
        solver = SWIProlog()

        head = c_pred("head", 2)
        tail = c_pred("tail", 2)
        take_second = c_pred("take_second", 2)
        H = c_var("Head")
        T = c_var("Tail")
        X = c_var("X")
        Y = c_var("Y")

        hatm1 = head(Pair(H, T), H)
        tatm1 = tail(Pair(H, T), T)
        cl = (take_second(X,Y) <= tail(X, T) & head(T, Y))

        solver.assertz(hatm1)
        solver.assertz(tatm1)
        solver.assertz(cl)

        l = List([1,2,3,4,5])
        print(solver.query(take_second(l, X)))

        del solver

    def test7(limit=50):
        pl = SWIProlog()

        p = c_pred("p", 2)
        f = c_functor("t", 3)
        f1 = p("a", "b")

        pl.assertz(f1)

        X = c_var("X")
        Y = c_var("Y")

        query = p(X, Y)

        r = pl.has_solution(query)
        print("has solution", r)

        rv = pl.query(query, time_limit=limit)
        print("all solutions", rv)

        f2 = p("a", "c")
        pl.assertz(f2)

        rv = pl.query(query, time_limit=limit)
        print("all solutions after adding f2", rv)

        func1 = f(1, 2, 3)
        f3 = p(func1, "b")
        pl.assertz(f3)

        rv = pl.query(query, time_limit=limit)
        print("all solutions after adding structure", rv)

        l = List([1, 2, 3, 4, 5])

        member = c_pred("member", 2)

        query2 = member(X, l)

        rv = pl.query(query2, time_limit=limit)
        print("all solutions to list membership ", rv)

        r = c_pred("r", 2)
        f4 = r("a", l)
        f5 = r("a", "b")

        pl.asserta(f4)
        pl.asserta(f5)

        query3 = r(X, Y)

        rv = pl.query(query3, time_limit=limit)
        print("all solutions after adding list ", rv)

        # Foreign predicates

        def hello(t):
            print("Foreign: Hello", t)

        hello_pred = pl.register_foreign(hello, 1)
        # print(hello_pred)

        f_query = hello_pred("a")

        pl.has_solution(f_query)

        del p

    def test8(limit=50):
        pl = SWIProlog()

        p = c_pred("p", 2)
        f = c_functor("t", 3)
        f1 = p("a", "b")

        pl.assertz(f1)

        X = c_var("X")
        Y = c_var("Y")

        query = p(X, Y)

        r = pl.has_solution(query)
        print("has solution", r)

        rv = pl.query(query, depth_limit=limit)
        print("all solutions", rv)

        f2 = p("a", "c")
        pl.assertz(f2)

        rv = pl.query(query, depth_limit=limit)
        print("all solutions after adding f2", rv)

        func1 = f(1, 2, 3)
        f3 = p(func1, "b")
        pl.assertz(f3)

        rv = pl.query(query, depth_limit=limit)
        print("all solutions after adding structure", rv)

        l = List([1, 2, 3, 4, 5])

        member = c_pred("member", 2)

        query2 = member(X, l)

        rv = pl.query(query2, depth_limit=limit)
        print("all solutions to list membership ", rv)

        r = c_pred("r", 2)
        f4 = r("a", l)
        f5 = r("a", "b")

        pl.asserta(f4)
        pl.asserta(f5)

        query3 = r(X, Y)

        rv = pl.query(query3, depth_limit=limit)
        print("all solutions after adding list ", rv)

        # Foreign predicates

        def hello(t):
            print("Foreign: Hello", t)

        hello_pred = pl.register_foreign(hello, 1)
        # print(hello_pred)

        f_query = hello_pred("a")

        pl.has_solution(f_query)

        del p

    def test9(limit=50):
        pl = SWIProlog()

        p = c_pred("p", 2)
        f = c_functor("t", 3)
        f1 = p("a", "b")

        pl.assertz(f1)

        X = c_var("X")
        Y = c_var("Y")

        query = p(X, Y)

        r = pl.has_solution(query)
        print("has solution", r)

        rv = pl.query(query, inference_limit=limit)
        print("all solutions", rv)

        f2 = p("a", "c")
        pl.assertz(f2)

        rv = pl.query(query, inference_limit=limit)
        print("all solutions after adding f2", rv)

        func1 = f(1, 2, 3)
        f3 = p(func1, "b")
        pl.assertz(f3)

        rv = pl.query(query, inference_limit=limit)
        print("all solutions after adding structure", rv)

        l = List([1, 2, 3, 4, 5])

        member = c_pred("member", 2)

        query2 = member(X, l)

        rv = pl.query(query2, inference_limit=limit)
        print("all solutions to list membership ", rv)

        r = c_pred("r", 2)
        f4 = r("a", l)
        f5 = r("a", "b")

        pl.asserta(f4)
        pl.asserta(f5)

        query3 = r(X, Y)

        rv = pl.query(query3, inference_limit=limit)
        print("all solutions after adding list ", rv)

        # Foreign predicates

        def hello(t):
            print("Foreign: Hello", t)

        hello_pred = pl.register_foreign(hello, 1)
        # print(hello_pred)

        f_query = hello_pred("a")

        pl.has_solution(f_query)

        del p

    def test10():

        pl = SWIProlog()

        p = c_pred("p", 2)
        a = c_pred("a", 2)

        f1 = p("a", "b")

        pl.assertz(f1)

        #cl1 = (a("X", "Y") <= p("X", "Y"))
        cl2 = (a("X", "Y") <= a("X", "Z") & p("Z", "Y"))

        #pl.assertz(cl1)
        pl.assertz(cl2)

        q = a("X", "Y")

        print(pl.query(q, time_limit=1))

        del pl





    #test1()
    #test2()
    #test4()
    #test5()
    #test6()
    #test7(limit=100)
    #test8(limit=5)
    #test9(limit=1)

    test10()











