//
// Created by Sebastijan Dumancic on 09/06/2020.
//

#include <pybind11/pybind11.h>  // has to be the first include, otherwise it doesn't compile
#include "SWI-Prolog.h"
#include <string.h>
#include <iostream>


using namespace std;
namespace py = pybind11;

PYBIND11_MODULE(swipy, m)
{
    m.attr("VARIABLE") = PL_VARIABLE;
    m.attr("ATOM") = PL_ATOM;
    m.attr("NIL") = PL_NIL;
    m.attr("STRING") = PL_STRING;
    m.attr("INTEGER") = PL_INTEGER;
    m.attr("FLOAT") = PL_FLOAT;
    m.attr("TERM") = PL_TERM;
    m.attr("LIST_PAIR") = PL_LIST_PAIR;
    m.attr("LIST") = PL_LIST;

    m.def("swipy_init", [](char *exec_path) {
       char *av[1];
       av[0] = (char *) exec_path;

       return PL_initialise(1, av);
    }, "initialises SWIPL engine");
    m.def("swipy_cleanup", &PL_cleanup, "cleans up the memroy");
    m.def("swipy_halt", &PL_halt, "halts SWIP");

    //atoms and functors
    m.def("swipy_new_atom", &PL_new_atom, "creates new atom");
    m.def("swipy_put_nil", &PL_put_nil, "puts nil in term");
    m.def("swipy_unify_nil", &PL_unify_nil, "unify term with nil");
    m.def("swipy_atom_chars", &PL_atom_chars, "returns the name of the atom");
    m.def("swipy_new_functor", &PL_new_functor, "create new functor from atom and arity");
    m.def("swipy_functor_name", &PL_functor_name, "returns the name of the functor (atom)");
    m.def("swipy_functor_arity", &PL_functor_arity, "returns the arity of the functor");

    //testing types
    m.def("swipy_term_type", &PL_term_type, "test term type");
    m.def("swipy_is_variable", &PL_is_variable, "is var?");
    m.def("swipy_is_ground", &PL_is_ground, "is ground?");
    m.def("swipy_is_atom", &PL_is_atom, "is atom?");
    m.def("swipy_is_string", &PL_is_string, "is string?");
    m.def("swipy_is_integer", &PL_is_integer, "is integer?");
    m.def("swipy_is_float", &PL_is_float, "is float?");
    m.def("swipy_is_compound", &PL_is_compound, "is compound?");
    m.def("swipy_is_functor", &PL_is_functor, "is functor?");
    m.def("swipy_is_list", &PL_is_list, "is list?");
    m.def("swipy_is_pair", &PL_is_pair, "is pair ");
    m.def("swipy_is_atomic", &PL_is_atomic, "is atomic?");
    m.def("swipy_is_number", &PL_is_number, "is number?");


    // getting data from terms
    m.def("swipy_get_atom", [](term_t term) {
        atom_t atm;
        PL_get_atom(term, &atm);

        return atm;
    }, "returns the atom of the term");
    m.def("swipy_get_integer", [](term_t term) {
        int i;
        PL_get_integer(term, &i);

        return i;
    }, "returns the integer value of the term");

    m.def("swipy_get_bool", [](term_t term) {
        int i;
        PL_get_bool(term, &i);
        return i;
    });
    m.def("swipy_get_atom_chars", [](term_t t) {
        char* name;
        PL_get_atom_chars(t, &name);
        return name;
    }, "get name of the atom");
    m.def("swipy_get_string_chars", [](term_t t) {
            char* val;
            int len;
            PL_get_string(t, &val, reinterpret_cast<size_t *>(&len));
            return val;
        }, "get string from the string const and length");
    m.def("swipy_get_float", [](term_t t){
        double f;
        PL_get_float(t, &f);
        return f;
        }, "get float from term");
    m.def("swipy_get_functor", [](term_t t) {
            functor_t f;
            PL_get_functor(t, &f);
            return f;
        },"return the functor");
    m.def("swipy_get_name_arity", [](term_t t){
            py::list l;
            atom_t name;
            size_t ar;
            PL_get_name_arity(t, &name, &ar);
            l.append(name);
            l.append(ar);
            return l;
        }, "returns the name and the arity of a compound");
    m.def("swipy_get_compound_name_arity", [](term_t t){
        py::list l;
        atom_t name;
        size_t ar;
        PL_get_compound_name_arity(t, &name, &ar);
        l.append(name);
        l.append(ar);
        return l;
        }, "get name and arity of a compound");
    m.def("swipy_get_arg", &PL_get_arg, "get arguments");
    m.def("swipy_get_list", &PL_get_list, "get list");
    m.def("swipy_get_head", &PL_get_head, "get head of a list");
    m.def("swipy_get_tail", &PL_get_tail, "get tail of a list");
    m.def("swipy_get_nil", &PL_get_nil, "get nil");


    // constructing terms
    m.def("swipy_new_term_ref", &PL_new_term_ref, "new term ref");
    m.def("swipy_new_term_refs", &PL_new_term_refs, "new term references");
    m.def("swipy_put_variable", &PL_put_variable, "put variable into term reference");
    m.def("swipy_put_atom", &PL_put_atom, "put atom into term reference");
    m.def("swipy_put_bool", &PL_put_bool, "put boolean into term reference");
    m.def("swipy_put_atom_chars", &PL_put_atom_chars, "put atom with name into term");
    m.def("swipy_put_string_chars", &PL_put_string_chars, "put string into term");
    m.def("swipy_put_integer", &PL_put_integer, "put int into term");
    m.def("swipy_put_float", &PL_put_float, "put float into term");
    m.def("swipy_put_functor", &PL_put_functor, "create a compound with functor and all args as vars");
    m.def("swipy_put_list", &PL_put_list, "create list into term");
    m.def("swipy_put_term", &PL_put_term, "put term into another term");
    m.def("swipy_cons_functor", [](term_t t, functor_t fnc, term_t args) {
        return PL_cons_functor_v(t, fnc, args);
    }, "constructs a term from a functor and arguments");
    m.def("swipy_cons_list", &PL_cons_list, "constructs list from head and tail");
    m.def("swipy_copy_term_ref", &PL_copy_term_ref, "copies a given term");

    // unification
    m.def("swipy_unify", &PL_unify, "unify two terms");
    m.def("swipy_unify_atom", &PL_unify_atom, "unify term with atom");
    m.def("swipy_unify_bool", &PL_unify_bool, "unify term with a bool");
    m.def("swipy_unify_atom_chars", &PL_unify_atom_chars, "unify term with an atom created from chars");
    m.def("swipy_unify_string_chars", &PL_unify_string_chars, "unify term with a string");
    m.def("swipy_unify_integer", &PL_unify_integer, "unify term with an integer");
    m.def("swipy_unify_float", &PL_unify_float, "unify term with a float");
    m.def("swipy_unify_compound", &PL_unify_compound, "unify compound with a functor");
    m.def("swipy_unify_list", &PL_unify_list, "unify term with head and tail");
    m.def("swipy_unify_nil", &PL_unify_nil, "unify term with nil");
    m.def("swipy_unify_arg", &PL_unify_arg, "unify n-th argument of t with a");


    // calling prolog
    m.def("swipy_predicate", &PL_predicate, "create predicate reference");
    m.def("swipy_open_query", [](predicate_t p, term_t t) {
        return PL_open_query(NULL, PL_Q_NORMAL, p, t);
    }, "opens a query");
    m.def("swipy_next_solution", &PL_next_solution, "go to the next solution");
    m.def("swipy_cut_query", &PL_cut_query, "cut the query");
    m.def("swipy_close_query", &PL_close_query, "close the query");

}