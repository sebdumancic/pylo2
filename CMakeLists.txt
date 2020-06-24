cmake_minimum_required(VERSION 3.16)
project(pylo)

set(CMAKE_CXX_STANDARD 17)

SET(SOURCE_DIR "pylo")
set(SOURCES "${SOURCE_DIR}/language.cpp")

option(CIAO "Compile Ciao" OFF)
option(GPROLOG "Compile GNU-Prolog" OFF)
option(XSBPROLOG "Compile XSB Prolog" OFF)
option(SWIPL "Compile SWI Prolog" OFF)

add_subdirectory(lib/pybind11)

if (CIAO)
pybind11_add_module(ciaopy ${SOURCES} "${SOURCE_DIR}/binding_ciao.cpp")

# CIAO THINGIES
include_directories(ciaopy /Users/seb/.ciaoroot/master/build/eng/ciaoengine/include)
link_libraries(ciaopy /Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64/libciaoengine.dylib)
link_directories(ciaopy /Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64)
target_link_libraries(ciaopy PUBLIC -L/Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64)
target_link_libraries(ciaopy PUBLIC libciaoengine.dylib)

add_compile_options(-Wall -Wextra -pedantic -v -undefined dynamic_lookup -fPIC -fno-stack-check -fno-strict-aliasing -O2 -fomit-frame-pointer   -D_REENTRANT -DTHREADS -DFOREIGN_FILES  -DDARWIN -Dx86_64  -DUSE_OWN_MALLOC  -DANDPARALLEL  -DTABLING -Wstrict-prototypes -Wl,-rpath -Wl,/Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64) #(-v -undefined dynamic_lookup) # -fPIC `python -m pybind11 --includes`)
endif (CIAO)

# GNU_PROLOG
if (GPROLOG)
    #set(GPROLOG_DIR  "/usr/local/gprolog-1.4.5")
    set(GPROLOG_DIR "$ENV{GNU_LIB_PATH}")
    include_directories("${GPROLOG_DIR}/include")
    include_directories("${GPROLOG_DIR}/lib")
    pybind11_add_module(pygprolog ${SOURCES} "${SOURCE_DIR}/binding_gprolog.cpp")

    link_libraries(${GPROLOG_DIR}/lib/libengine_pl.a)
    target_link_directories(pygprolog PUBLIC "${GPROLOG_DIR}/lib")
    target_link_libraries(pygprolog PUBLIC "${GPROLOG_DIR}/lib/libengine_pl.a")
    target_link_libraries(pygprolog PUBLIC "${GPROLOG_DIR}/lib/all_pl_bips.o")
    target_link_libraries(pygprolog PUBLIC "${GPROLOG_DIR}/lib/all_fd_bips.o")
    target_link_libraries(pygprolog PUBLIC "${GPROLOG_DIR}/lib/debugger.o")
    target_link_libraries(pygprolog PUBLIC "${GPROLOG_DIR}/lib/libbips_fd.a")
    target_link_libraries(pygprolog PUBLIC "${GPROLOG_DIR}/lib/libbips_pl.a")
    target_link_libraries(pygprolog PUBLIC "${GPROLOG_DIR}/lib/liblinedit.a")
    target_link_libraries(pygprolog PUBLIC "${GPROLOG_DIR}/lib/libengine_fd.a")
    #target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/toplevel.o)
    #target_link_libraries(pygprolog PUBLIC /usr/local/gprolog-1.4.5/lib/toplevel_main.o)
    #target_link_libraries(pygprolog PUBLIC /Users/seb/Documents/programs/gprolog-1.4.5/pylo/libengine_fd.a)

add_compile_options(-Wall -Wextra -pedantic -v -undefined dynamic_lookup -fPIC)
endif(GPROLOG)

# XSB PROLOG
if(XSBPROLOG)
    #set(XSB_HOME_DIR "/Users/seb/Documents/programs/XSB")
    #set(XSB_FULL_DIR "/Users/seb/Documents/programs/XSB/config/i386-apple-darwin18.7.0")
    set(XSB_HOME_DIR "$ENV{XSB_LIB_PATH}/../..")
    set(XSB_FULL_DIR "$ENV{XSB_LIB_PATH}")
    pybind11_add_module(pyxsb ${SOURCES} "${SOURCE_DIR}/binding_xsbprolog.cpp")
    include_directories("${XSB_HOME_DIR}/emu")
    #include_directories("${XSB_HOME_DIR}/config/i386-apple-darwin18.7.0")
    include_directories("${XSB_FULL_DIR}")
    #link_libraries(pyxsb PUBLIC "${XSB_HOME_DIR}/config/i386-apple-darwin18.7.0/saved.o")
    link_libraries(pyxsb PUBLIC "${XSB_FULL_DIR}/saved.o")
    #target_link_libraries(pyxsb PUBLIC "${XSB_HOME_DIR}/config/i386-apple-darwin18.7.0/saved.o/xsb.o")
    target_link_libraries(pyxsb PUBLIC "${XSB_FULL_DIR}/saved.o/xsb.o")
    add_compile_options(-O3 -fno-strict-aliasing -v -undefined dynamic_lookup -fPIC -Wall -pipe )
endif(XSBPROLOG)

if(SWIPL)
    #set(SWIPL_HOME "/usr/local/Cellar/swi-prolog/8.2.0")
    #set(SWIPL_FULL_HOME "/usr/local/Cellar/swi-prolog/8.2.0/libexec/lib/swipl")
    set(SWIPL_HOME "$ENV{SWIPL_LIB_PATH}/../..")
    set(SWIPL_FULL_HOME "$ENV{SWIPL_LIB_PATH}")
    pybind11_add_module(swipy ${SOURCES} "${SOURCE_DIR}/binding_swipl.cpp")
    include_directories("${SWIPL_HOME}/include")
    #link_libraries(swipy PUBLIC "${SWIPL_HOME}/lib/x86_64-darwin/libswipl.dylib")
    link_libraries(swipy PUBLIC "${SWIPL_FULL_HOME}/libswipl.dylib")
    #target_link_libraries(swipy PUBLIC "${SWIPL_HOME}/lib/x86_64-darwin/libswipl.dylib")
    target_link_libraries(swipy PUBLIC "${SWIPL_FULL_HOME}/libswipl.dylib")
endif(SWIPL)

#if(YAPPROLOG)
#    pybind11_add_module(yapy ${SOURCES} "${SOURCE_DIR}/binding_yap.cpp")
#    include_directories(/Users/seb/Documents/programs/yap-6.3/include)
#    link_libraries(yapy PUBLIC /Users/seb/Documents/programs/yap-6.3/arch/libYap.a)
#    target_link_libraries(yapy PUBLIC /Users/seb/Documents/programs/yap-6.3/arch/libYap.a)
#endif(YAPPROLOG)

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
