//
// Created by Sebastijan Dumancic on 24/05/2020.
//

#include <pybind11/pybind11.h>
//#include "language.h"
#include "gprolog.h"
//#include <vector>

//#include <pybind11/stl.h>
//#include <unordered_map>

using namespace std;

namespace py = pybind11;


void start_gprolog();


void start_gprolog() {
    const char *defaults[] = {"gprolog"};
    Pl_Start_Prolog(1, const_cast<char **>(defaults));
}

py::list read_list(PlTerm term) {
    py::list elements;

    int listLength = Pl_List_Length(term);

    PlTerm *elemts;
    elemts = Pl_Rd_List(term);

    while (listLength > 0) {
        PlTerm head = *(elemts + 0);
        PlTerm tail = *(elemts + 1);
        elements.append(head);
        elemts = Pl_Rd_List(tail);
        listLength -= 1;
    }

    return elements;
}






PYBIND11_MODULE(pygprolog, m) {
    // basic data structures

    py::enum_<PlBool>(m, "PlBool")
            .value("True", PL_TRUE)
            .value("False", PL_FALSE)
            .export_values();

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

    // reading terms
    m.def("pygp_Rd_Integer", &Pl_Rd_Integer, "read integer value of the term");
    m.def("pygp_Rd_Decimal", &Pl_Rd_Float, "read decimal value of the term");
    m.def("pygp_Rd_String", &Pl_Rd_String, "read the string from the term");
    m.def("pygp_Rd_List", &read_list, "read the elements of the list");


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
    m.def("pygp_Mk_List", [](const py::list &args) {
        PlTerm previousList = Pl_Mk_List(NULL);

        int listSize = args.size();
        //PlTerm argsToUse[listSize];

        for(int i = listSize - 1; i >= 0; i--) {
            PlTerm headTail[2] = {args[i].cast<PlTerm>(), previousList};
            previousList = Pl_Mk_List(headTail);
        }

        return previousList;


//        for(int i=0; i < args.size(); i++) {
//            argsToUse[listSize - 1 - i] = args[i].cast<PlTerm>();
//        }

//        return Pl_Mk_List(argsToUse);
        }, "creates list from an array of args");
    m.def("pygp_Mk_Compound", [](int functor, int arity, const py::list &args) {
            PlTerm argsToUse[arity];

            for(int i=0; i < arity; i++) {
                argsToUse[i] = args[i].cast<PlTerm>();
            }

            return Pl_Mk_Compound(functor, arity, argsToUse);

        }, "creates a compound from the functor, arity and a list of args");

    // checking the types of terms
    m.def("pygp_Builtin_Var", &Pl_Builtin_Var, "checks if the term is a variable");
    m.def("pygp_Builtin_Non_Var", &Pl_Builtin_Non_Var, "is term not a variable?");
    m.def("pygp_Builtin_Atom", &Pl_Builtin_Atom, "is term an atom");
    m.def("pygp_Builtin_Integer", &Pl_Builtin_Integer, "is term an integer");
    m.def("pygp_Builtin_Float", &Pl_Builtin_Float, "is term a float");
    m.def("pygp_Builtin_Number", &Pl_Builtin_Number, "is term a number");
    m.def("pygp_Builtin_Atomic", &Pl_Builtin_Atomic, "is term atomic");
    m.def("pygp_Builtin_Compound", &Pl_Builtin_Compound, "is term a compound");
    m.def("pygp_Builtin_Callable", &Pl_Builtin_Callable, "is term callable");
    m.def("pygp_Builtin_List", &Pl_Builtin_List, "is term a list");
    m.def("pygp_Builtin_Partial_List", &Pl_Builtin_Partial_List, "is term a partial list");
    m.def("pygp_Builtin_List_Or_Partial_List", &Pl_Builtin_List_Or_Partial_List);
    m.def("pygp_Type_Of_Term", [](PlTerm term) {
            int res;
            res = Pl_Type_Of_Term(term);

            if (res == PL_PLV) {
                return 1;
            }
            else if (res == PL_FDV) {
                return 2;
            }
            else if (res == PL_INT) {
                return 3;
            }
            else if (res == PL_FLT) {
                return 4;
            }
            else if (res == PL_ATM) {
                return 5;
            }
            else if (res == PL_LST) {
                return 6;
            }
            else {
                return 7;
            }

        }, "return type of term");
    m.def("pygp_List_Length", &Pl_List_Length, "returns the length of the list");


    // comparing prolog terms


    // builtin functors: functor, arg, =..
    m.def("pygp_Builtin_Functor", &Pl_Builtin_Functor, "maps term to the functor and arity");
    m.def("pygp_Builtin_Arg", &Pl_Builtin_Arg, "gets the arg_no from term ");
    m.def("pygp_Builtin_Univ", &Pl_Builtin_Univ, "performs =..");

    // comparing arithmetic expressions

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