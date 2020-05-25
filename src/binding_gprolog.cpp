//
// Created by Sebastijan Dumancic on 24/05/2020.
//

#include <pybind11/pybind11.h>
#include "language.h"
#include "gprolog.h"

//#include <pybind11/stl.h>
//#include <unordered_map>

using namespace std;

namespace py = pybind11;

void start_gprolog() {
    const char *defaults[] = {"abc"};
    Pl_Start_Prolog(1, const_cast<char **>(defaults));
}


PYBIND11_MODULE(pygprolog, m) {
    // basic data structures
    py::class_<Term>(m, "Term")
            .def(py::init<const std::string &>())
            .def("getName", &Term::getName);

    py::class_<Const, Term>(m, "Const")
            .def(py::init<const std::string &>())
            .def("getName", &Const::getName);

    py::class_<Integer, Const>(m, "Integer")
            .def(py::init<int>())
            .def("getName", &Integer::getName)
            .def("getValue", &Integer::getValue);

    py::class_<Decimal, Const>(m, "Decimal")
            .def(py::init<double>())
            .def("getName", &Decimal::getName)
            .def("getValue", &Decimal::getValue);

    py::class_<Var, Term>(m, "Var")
            .def(py::init<const string &>())
            .def("getName", &Var::getName);

    py::class_<Functor>(m, "Functor")
            .def(py::init<const string &, int>())
            .def("getName", &Functor::getName)
            .def("getArity", &Functor::getArity);

    py::class_<Structure, Term>(m, "Structure")
            .def(py::init<Functor, std::vector<Term *>>())
            .def("getFunctor", &Structure::getFunctor)
            .def("getName", &Structure::getName)
            .def("getArguments", &Structure::getArguments);

    py::class_<List, Term>(m, "List")
            .def(py::init<std::vector<Term *>>())
            .def("getElements", &List::getElements)
            .def("getHead", &List::getHead)
            .def("getTail", &List::getTail);

    // basic vars -- DOESNT WORK PROPERLY
//    m.attr("pygp_true") = PL_TRUE;
//    m.attr("pygp_false") = PL_FALSE;
//    m.attr("pygp_fail") = PL_FALSE;
//    m.attr("pygp_success") = PL_SUCCESS;
//    m.attr("pygp_exception") = PL_EXCEPTION;
//    m.attr("pygp_recover") = PL_RECOVER;
//    m.attr("pygp_cut") = PL_CUT;
//    m.attr("pygp_keep_for_prolog") = PL_KEEP_FOR_PROLOG;



    // managing prolog atoms
    m.def("pygp_Atom_Name", &Pl_Atom_Name, "Returns the internal name of the atom");
    m.def("pygp_Atom_Length", &Pl_Atom_Length, "Returns the length of the name of an atom");
    m.def("pygp_Create_Atom", &Pl_Create_Atom, "Creates an atom with the given name");
    m.def("pygp_Is_Valid_Atom", &Pl_Is_Valid_Atom, "Returns true if the given name corresponds to an existing atom (the string with the name should not be changed later)");
    m.def("pygp_Create_Allocate_Atom", &Pl_Create_Allocate_Atom, "Creates an atom with copy of the name");
    m.def("pygp_Find_Atom", &Pl_Find_Atom, "returns the internal key of the atom with the given name");
    m.def("pygp_Atom_Char", &Pl_Atom_Char, "Create an atom with a single character in name");
    m.def("pygp_Atom_Nil", &Pl_Atom_Nil, "Returns the empty list");
    m.def("pygp_Atom_False", &Pl_Atom_False, "Returns false");
    m.def("pygp_Atom_True", &Pl_Atom_True, "returns true");
    m.def("pygp_Atom_End_Of_File", &Pl_Atom_End_Of_File, "end of file character");

    // unification
    m.def("pygp_Unif", &Pl_Unif, "Performs unification of two terms");
    m.def("pygp_Unif_With_Occurs_Check", &Pl_Unif_With_Occurs_Check, "performs unification with occurs check");
    m.def("pygp_Un_List_Check", &Pl_Un_List_Check, "unifies a list of terms with a term");
    m.def("pygp_Un_Compound_Check", &Pl_Un_Compound_Check, "unifies [functor, arity, args] with a term");
    m.def("pygp_Un_Proper_List_Check", &Pl_Un_Proper_List_Check, "unifies [size, list of args] a term");

    // creating terms
    m.def("pygp_Mk_Integer", &Pl_Mk_Integer, "Creates an integer term");
    m.def("pygp_Mk_Float", &Pl_Mk_Float, "Creates the float term");
    m.def("pygp_Mk_Variable", &Pl_Mk_Variable, "Creates new variable");
    m.def("pygp_Mk_Number", &Pl_Mk_Number, "Creates a number term");
    m.def("pygp_Mk_Atom", &Pl_Mk_Atom, "Turns an atom into a term");
    m.def("pygp_Mk_String", &Pl_Mk_String, "Creates string term");
    m.def("pygp_Mk_Proper_List", &Pl_Mk_Proper_List, "creates a list of n arguments and the list of args");
    m.def("pygp_Mk_List", &Pl_Mk_List, "creates list from an array of args");
    m.def("pygp_Mk_Compound", [](int functor, int arity, const py::list &args) {
            PlTerm argsToUse[arity];

            for(int i=0; i < arity; i++) {
                argsToUse[i] = args[i].cast<PlTerm>();
            }

            return Pl_Mk_Compound(functor, arity, argsToUse);

        }, "creates a compound from the functor, arity and a list of args");

    // checking the types of terms

    // builtin functors: functor, arg, =..
    m.def("pygp_Builtin_Functor", &Pl_Builtin_Functor, "maps term to the functor and arity");
    m.def("pygp_Builtin_Arg", &Pl_Builtin_Arg, "gets the arg_no from term ");
    m.def("pygp_Builtin_Univ", &Pl_Builtin_Univ, "performs =..");

    // query manipulation
    m.def("pygp_Query_Begin", []() {
            Pl_Query_Begin(PL_TRUE);
        }, "Starts the query");
    m.def("pygp_Query_Call", [](int func, int arity, const py::list& args) {
            PlTerm argsToUse[arity];

            for(int i = 0; i < arity; i++) {
                argsToUse[i] = args[i].cast<PlTerm>();
            }

            return Pl_Query_Call(func, arity, argsToUse);
        }, "calls the predicate passing the args");
    m.def("pygp_Query_Start", [](int func, int arity, const py::list& args) {
            PlTerm argsToUse[arity];

            for(int i = 0; i < arity; i++) {
                argsToUse[i] = args[i].cast<PlTerm>();
            }

            return Pl_Query_Start(func, arity, argsToUse, PL_TRUE);
        }, "opens and calls the query");
    m.def("pygp_Query_Next_Solution", &Pl_Query_Next_Solution, "next solution");
    m.def("pygp_Query_End", []() {
            Pl_Query_End(PL_TRUE);
        }, "end the query");


    // managing the prolog engine
    m.def("pygp_Start_Prolog", &start_gprolog, "starts the prolog engine");
    m.def("pygp_Stop_Prolog", &Pl_Stop_Prolog, "stops the engine");
    m.def("pygp_Reset_Prolog", &Pl_Reset_Prolog, "reset the engine");


}