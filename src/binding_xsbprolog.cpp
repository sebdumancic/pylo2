//
// Created by Sebastijan Dumancic on 05/06/2020.
//
#include <pybind11/pybind11.h>  // has to be the first include, otherwise it doesn't compile
#include "cinterf.h"
//#include <string.h>
#include <iostream>


using namespace std;
namespace py = pybind11;

PYBIND11_MODULE(pyxsb, m)
{
    m.attr("SUCCESS") = XSB_SUCCESS;
    m.attr("ERROR") = XSB_ERROR;
    m.attr("FAILURE") = XSB_FAILURE;
    m.attr("OVERFLOW") = XSB_OVERFLOW;
    m.attr("WARNING") = XSB_WARNING;

    m.def("pyxsb_init_string", [](const string& exec) {
            if (xsb_init_string(const_cast<char *>(exec.c_str())) == XSB_ERROR) {
                cout << "++initializing XSB: " << xsb_get_init_error_type() << " | " << xsb_get_init_error_message();
                //exit(XSB_ERROR);
            }
        }, "initialise XSB prolog engine");
    m.def("pyxsb_close", &xsb_close, "closes XSB prolog engine");
    m.def("pyxsb_command_string", &xsb_command_string);

    m.def("pyxsb_query_string", [](char *query) {
            XSB_StrDefine(return_string);
            int rc;
            rc = xsb_query_string_string(query, &return_string, const_cast<char *>(";"));

            if (rc == XSB_SUCCESS){
                return return_string.string;
            }
            else {
                return const_cast<char *>("");
            }

        }, "opens a query over string");
    //m.def("pyxsb_query_string_string", &xsb_query_string_string, "opens a query over string and context");
    m.def("pyxsb_next_string", []() {
            XSB_StrDefine(return_string);
            int rc;
            rc = xsb_next_string(&return_string, const_cast<char *>(";"));

            if (rc == XSB_SUCCESS) {
                return return_string.string;
            }
            else {
                return const_cast<char *>("");
            }

        }, "goes to the next solution");
    m.def("pyxsb_close_query", &xsb_close_query, "closes the current query");

}
