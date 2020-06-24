Python wrappers around Prolog engines

# Engines

Engines to use:

  - [ ] [Ciao Prolog](https://ciao-lang.org/) and its [C interface](https://ciao-lang.org/ciao/build/doc/ciao.html/foreign_interface_doc.html) 
  - [ ] [B-Prolog](http://www.picat-lang.org/bprolog) and [C interface](http://www.picat-lang.org/bprolog/download/manual.pdf)
  - [x] [SWIPL](https://www.swi-prolog.org/) and [C interface](https://www.swi-prolog.org/pldoc/man?section=foreign)
  - [ ] [YAP](http://cracs.fc.up.pt/~nf/Docs/Yap/yap.html) and [C interface](http://cracs.fc.up.pt/~nf/Docs/Yap/yap.html#SEC150)
  - [x] GNU Prolog and [C interface](http://www.gprolog.org/manual/gprolog.html#sec335)
  - [x] XSB PRolog and C interface
  - [ ] [FASSIL](https://dectau.uclm.es/fasill/)
  - [ ] [TauProlog](http://tau-prolog.org/)  (with [pyv8](https://code.google.com/archive/p/pyv8/))
  - [ ] [Bousi Prolog](https://dectau.uclm.es/bousi-prolog/)


# Installation

## Manual

Pylo relies on ENV variables to configure identify the needed libraries.

To install the support for **GNU Prolog**, you need to provide the path to the GNu-prolog's installation folder through the `GNU_LIB_PATH`.
For instance, using the default installation on OSC results in the following path
```shell script
export GNU_LIB_PATH=/usr/local/gprolog-1.4.5
``` 


To install the support for **XSB Prolog**, you need to provide the path to the foreign interface library through the `XSB_LIB_PATH`.
To locate this folder, assume that `<XSB_ROOT>` contains the folder in which the XSB source was unpacked.
```shell script
export XSB_LIB_PATH=<XSB_ROOT>/config/<arch>
```
where `<arch>` is the architecture of your system (it will be the only folder in `<XSB_ROOT>/config` folder).


To install the support for **SWI Prolog**, you need to provide the path to the SWIPL library through the `SWIPL_LIB_PATH`.
To find the right folder, look for the `lib/<arch>` folder in the SWIPL installation folder (`<arch>` is the architecture of you system).
For instance, on OSX the EVN var should look like this
```shell script
export SWIPL_LIB_PATH=/usr/local/Cellar/swi-prolog/8.2.0/libexec/lib/swipl/lib/x86_64-darwin
``` 


Once the environment variables have been setup, you can install `pylo` (and the desired Prolog engines) with the following commands

```shell script
mkdir build
cd build
cmake .. -D<prolog engine options>
make 
```

The takes the following form:
 - `-DGPROLOG=ON` to install the support for GNU-Prolog
 - `-DXSBPROLOG=ON` to install the support for XSB Prolog
 - `-DSWIPL=ON` to install the support for SWI Prolog
 
**Important:** due to the incompatibility of the compiling options, you cannot specify all three options at the same time. 
If you want to build the support for several Prolog engines, you have to compile the engines separately (with only one flag specified at the time).


Once the compilation is done, make sure that the `build` folder is accessible through the `PATH` and `PYTHONPATH` variables.




## Other practical considerations

 - In order to use SWIPL, you need to provide a path to the dynamic library using the `LD_LIBRARY_PATH` env var. For instance, on OSX 
 ```shell script
    export LD_LIBRARY_PATH=/usr/local/Cellar/swi-prolog/8.2.0/libexec/lib/swipl/lib/x86_64-darwin
```
 - For Ciao prolog, you also need to be able to find the dynamic library. On OSX
```shell script
    export LD_LIBRARY_PATH=/Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64/
```


# Usage






# Missing features

 - [ ] remember all created variables, so that they can be properly bound to the objects in the language
 - [ ] providing python functions as predicates
 - [ ] documentation
   - [ ] high-level engine
   - [ ] low-level primitives > ovo je malo uvredljivo, ciki