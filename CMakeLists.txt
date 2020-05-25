cmake_minimum_required(VERSION 3.16)
project(ciaopy)

set(CMAKE_CXX_STANDARD 17)

SET(SOURCE_DIR "src")
set(SOURCES "${SOURCE_DIR}/language.cpp")

option(CIAO "Compile Ciao" OFF)
option(GPROLOG "Compile GNU-Prolog" ON)

add_subdirectory(lib/pybind11)

if (CIAO)
pybind11_add_module("${PROJECT_NAME}" ${SOURCES} "${SOURCE_DIR}/binding_ciao.cpp")


# CIAO THINGIES
include_directories("${PROJECT_NAME}" /Users/seb/.ciaoroot/master/build/eng/ciaoengine/include)
link_libraries("${PROJECT_NAME}" /Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64/libciaoengine.dylib)
link_directories("${PROJECT_NAME}" /Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64)
target_link_libraries("${PROJECT_NAME}" PUBLIC -L/Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64)
target_link_libraries("${PROJECT_NAME}" PUBLIC libciaoengine.dylib)

add_compile_options(-Wall -Wextra -pedantic -v -undefined dynamic_lookup -fPIC -fno-stack-check -fno-strict-aliasing -O2 -fomit-frame-pointer   -D_REENTRANT -DTHREADS -DFOREIGN_FILES  -DDARWIN -Dx86_64  -DUSE_OWN_MALLOC  -DANDPARALLEL  -DTABLING -Wstrict-prototypes -Wl,-rpath -Wl,/Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64) #(-v -undefined dynamic_lookup) # -fPIC `python -m pybind11 --includes`)
endif (CIAO)

# GNU_PROLOG
if (GPROLOG)
    set(GPROLOG_DIR  "/usr/local/gprolog-1.4.5")
    set(GPROLOG_SRC /Users/seb/Documents/programs/gprolog-1.4.5/src)
    include_directories(/usr/local/gprolog-1.4.5/include)
    include_directories(/usr/local/gprolog-1.4.5/lib)
    pybind11_add_module(pygprolog ${SOURCES} "${SOURCE_DIR}/binding_gprolog.cpp")

    link_libraries(${GPROLOG_DIR}/lib/libengine_pl.a)
    target_link_directories(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib)
    target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/libengine_pl.a)
    target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/all_pl_bips.o)
    target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/all_fd_bips.o)
    target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/debugger.o)
    target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/libbips_fd.a)
    target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/libbips_pl.a)
    target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/liblinedit.a)
    target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/libengine_fd.a)
    #target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/toplevel.o)
    #target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/toplevel_main.o)
    #target_link_libraries(pygprolog PUBLIC /Users/seb/Documents/programs/gprolog-1.4.5/src/libengine_fd.a)

add_compile_options(-Wall -Wextra -pedantic -v -undefined dynamic_lookup -fPIC)
endif(GPROLOG)


#option(BUILD_TESTS "Build C++ test files" OFF)
#if (BUILD_TESTS)
#    # SET(TEST_DIR "tests")
#    SET(TESTS
#            "${SOURCE_DIR}/test-ciaopy.cpp")
#
#    # Generate a test executable
#    #include_directories(lib/catch/include)
#    add_executable("test${PROJECT_NAME}" ${TESTS})
#    # target_link_libraries("test${PROJECT_NAME}" PRIVATE ${PROJECT_NAME})
#    # target_link_libraries("test${PROJECT_NAME}" CiaoLib)
#endif (BUILD_TESTS)
