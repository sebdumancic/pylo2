//
// Created by Sebastijan Dumancic on 09/06/2020.
//

#include <pybind11/pybind11.h>  // has to be the first include, otherwise it doesn't compile
#include "YapInterface.h"
//#include <string.h>
#include <iostream>


using namespace std;
namespace py = pybind11;

PYBIND11_MODULE(yapy, m) {

    // init engine
    m.def("yapy_init", &YAP_FastInit, "initialise yap engine");

}