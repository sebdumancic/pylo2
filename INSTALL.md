# Installation

## Installation with pip

**STEP 1:** `pylo` relies on ENV variables to detect which Prolog engines to support.
The desired Prolog engines need to be installed first.

To install the support for **GNU Prolog**, you need to provide the `GNUPROLOG_HOME` variable pointing to the installation folder of GNU Prolog:
```shell script
# For OSX with default configuration (installed from sources)
export GNUPROLOG_HOME=/usr/local/gprolog-1.4.5
# On Ubuntu
export GNUPROLOG_HOME=/usr/lib/gprolog-1.4.5
```
You are looking for the folder that contains the following:
```text
COPYING     NEWS        VERSION     doc         gprolog.ico lib
ChangeLog   README      bin         examples    include
```



To install the support for **XSB_PROLOG**, you need to provide `XSB_HOME` variable pointing to the source of XSB Prolog.
This is the folder in which you unpacked the XSB source files.
For example
```shell script
export XSB_HOME=/Users/user/Documents/programs/XSB
```
You are looking for a folder that contains the following:
```text
FAQ             README          cmplib          etc             lib             site
InstallXSB.jar  admin           config          examples        packages        syslib
LICENSE         bin             docs            gpp             prolog-commons
Makefile        build           emu             installer       prolog_includes
```

To install the support for **SWI Prolog**, you need to provide `SWIPL_HOME` variable pointing to the installation folder of SWIPL.
On OSX, this looks like
```shell script
# on OSX, (installed from Homebrew)
export SWIPL_HOME=/usr/local/Cellar/swi-prolog/8.2.0/libexec/lib/swipl
```
You are looking for that contains the following items:
```text
LICENSE    README.md  bin        boot       boot.prc   customize  demo       doc        include    lib        library    swipl.home
```
On Ubuntu, it should be enough to set it to `/usr/lib`
```shell script
# On Ubuntu, installed from the repository
export SWIPL_HOME=/usr/lib
```
This folder should contain `libswipl.so` (Linux) file and the `swi-prolog` folder. 


**STEP 2:** Clone this repository. You need to pull it recursively to get the submodules.
```shell script
git clone https://github.com/sebdumancic/pylo2.git
git submodule init
git submodule update
```


**STEP 3:** Move to the folder you cloned the repository to.
Execute
```shell script
pip install --verbose .
```
or
```shell script
python setup.py install
```

That's it! You should be able to use Pylo now.


**STEP 4 (optional):** Test
```python
from pylo.tests import all_swipl_tests, all_gnu_tests, all_xsb_tests, test_kanren, test_datalog

all_swipl_tests()
all_gnu_tests()
all_xsb_tests("[path_to_XSB_folder]")  # the same folder for installation
test_kanren()
test_datalog()
```




## Manual

**STEP 1:** Pylo relies on ENV variables to configure identify the needed libraries.

To install the support for **GNU Prolog**, you need to provide the path to the GNu-prolog's installation folder through the `GNU_LIB_PATH`.
For instance, using the default installation on OSX results in the following path
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


**STEP 2:** Once the environment variables have been setup, you can install `pylo` (and the desired Prolog engines) with the following commands

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


**STEP 3:** Once the compilation is done, make sure that the `build` folder is accessible through the `PATH` and `PYTHONPATH` variables.





## Other practical considerations

 - In order to use SWIPL, you need to provide a path to the dynamic library using the `LD_LIBRARY_PATH` env var. For instance, on OSX 
 ```shell script
    export LD_LIBRARY_PATH=/usr/local/Cellar/swi-prolog/8.2.0/libexec/lib/swipl/lib/x86_64-darwin
```
 - For Ciao prolog, you also need to be able to find the dynamic library. On OSX
```shell script
    export LD_LIBRARY_PATH=/Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64/
```
 - Z3Py scripts stored in arbitrary directories can be executed if the 'build/python' directory is added to the PYTHONPATH environment variable and the 'build' directory is added to the DYLD_LIBRARY_PATH environment variable