cmake_minimum_required(VERSION 3.10)
project(pylo)

set(CMAKE_CXX_STANDARD 17)

SET(SOURCE_DIR "src/pylo")
#set(SOURCES "${SOURCE_DIR}/language.cpp")

option(CIAO "Compile Ciao" OFF)
option(GPROLOG "Compile GNU-Prolog" OFF)
option(XSBPROLOG "Compile XSB Prolog" OFF)
option(SWIPL "Compile SWI Prolog" OFF)

message("building:\n\tGNU PROLOG: ${GPROLOG}\n\tXSB PROLOG: ${XSBPROLOG}\n\tSWIPL: ${SWIPL}")

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

if (UNIX AND NOT APPLE)
    message("Compiling for Linux!")
endif()

if (APPLE)
    message("Compiling for Mac!")
endif()

# GNU_PROLOG
if (GPROLOG)
    #set(GPROLOG_DIR  "/usr/local/gprolog-1.4.5")
    set(GPROLOG_DIR "$ENV{GNU_LIB_PATH}")

    if(APPLE)
        set(GPROLOG_TO_USE "${GPROLOG_DIR}/lib")
        include_directories("${GPROLOG_DIR}/include")
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
        target_compile_options(pygprolog PUBLIC -Wall -Wextra -pedantic -v -undefined dynamic_lookup -fPIC)
    else()
        include_directories("${GPROLOG_DIR}/include")
        include_directories("${GPROLOG_DIR}")
        pybind11_add_module(pygprolog ${SOURCES} "${SOURCE_DIR}/binding_gprolog.cpp")

        link_libraries(${GPROLOG_DIR}/lib/libengine_pl.a)
        target_link_directories(pygprolog PUBLIC "${GPROLOG_DIR}")
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
        target_compile_options(pygprolog PUBLIC -Wall -Wextra -pedantic -v -fPIC)

    endif()


#add_compile_options(-Wall -Wextra -pedantic -v -undefined dynamic_lookup -fPIC)
endif(GPROLOG)

# XSB PROLOG
if(XSBPROLOG)
    #set(XSB_HOME_DIR "/Users/seb/Documents/programs/XSB")
    # set(XSB_FULL_DIR "/Users/seb/Documents/programs/XSB/config/i386-apple-darwin18.7.0")
    # set(XSB_HOME_DIR "${XSB_FULL_DIR}/../..")
    # GENERAL SETUP
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
    #add_compile_options(-O3 -fno-strict-aliasing -v -undefined dynamic_lookup -fPIC -Wall -pipe )
    if(APPLE)
        target_compile_options(pyxsb PUBLIC -O3 -fno-strict-aliasing -v -undefined dynamic_lookup -fPIC -Wall -pipe)
    else()
        target_compile_options(pyxsb PUBLIC -O3 -fno-strict-aliasing -v -fPIC -Wall -pipe)
    endif()
endif(XSBPROLOG)

if(SWIPL)

    pybind11_add_module(swipy ${SOURCES} "${SOURCE_DIR}/binding_swipl.cpp")

    message(STATUS "Getting SWI Prolog header and .so location")
    message(STATUS "$ swipl --dump-runtime-variables")

    execute_process(COMMAND swipl --dump-runtime-variables
      OUTPUT_VARIABLE swipl_runtime_result
      TIMEOUT 10)

    string(REPLACE "\"" "" swipl_variables ${swipl_runtime_result})
    string(REPLACE "\n" ";" swipl_variables2 ${swipl_variables})

    foreach(line IN ITEMS ${swipl_variables2})
      if(${line} MATCHES "PLBASE=.*")
        string(SUBSTRING ${line} 7 -1 SWIPL_FULL_HOME)
        message(STATUS "Path to swipl directory: ${SWIPL_FULL_HOME}")
      endif()
      if(${line} MATCHES "PLLIBDIR=.*")
        string(SUBSTRING ${line} 9 -1 SWIPL_SO_DIR)
        message(STATUS "Path to shared object directory: ${SWIPL_SO_DIR}")
      endif()
    endforeach(line)

    if(UNIX AND NOT APPLE)
        message(STATUS "Checking that libswipl.so exists")
        if(NOT EXISTS "${SWIPL_SO_DIR}/libswipl.so")
          message(FATAL_ERROR "Could not find libswipl.so in ${SWIPL_SO_DIR}")
        endif()

        include_directories("${SWIPL_FULL_HOME}/include")
        include_directories("${SWIPL_SO_DIR}")
        link_libraries(swipy PUBLIC "${SWIPL_SO_DIR}/libswipl.so")
        target_link_libraries(swipy PUBLIC "${SWIPL_SO_DIR}/libswipl.so")
    else()
        message(STATUS "Checking that libswipl.dylib exists")
        if(NOT EXISTS "${SWIPL_SO_DIR}/libswipl.dylib")
          message(FATAL_ERROR "Could not find libswipl.dylib in ${SWIPL_SO_DIR}")
        endif()

        include_directories("${SWIPL_FULL_HOME}/include")
        link_libraries(swipy PUBLIC "${SWIPL_SO_DIR}/libswipl.dylib")
        target_link_libraries(swipy PUBLIC "${SWIPL_SO_DIR}/libswipl.dylib")
    endif()

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
