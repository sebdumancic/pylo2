Python wrappers around Prolog engines

# Engines

Supported Prolog engines:
 - [SWIPL](https://www.swi-prolog.org/)
 - [GNU Prolog](http://www.gprolog.org)
 - [XSB Prolog](http://xsb.sourceforge.net/) 
 
Under development:
 - [ ] [Ciao Prolog](https://ciao-lang.org/) and its [C interface](https://ciao-lang.org/ciao/build/doc/ciao.html/foreign_interface_doc.html)
 - [ ] [TauProlog](http://tau-prolog.org/)  (with [pyv8](https://code.google.com/archive/p/pyv8/)) 
 
Maybe supported in the future:
  - [ ] [B-Prolog](http://www.picat-lang.org/bprolog) and [C interface](http://www.picat-lang.org/bprolog/download/manual.pdf)
  - [ ] [YAP](http://cracs.fc.up.pt/~nf/Docs/Yap/yap.html) and [C interface](http://cracs.fc.up.pt/~nf/Docs/Yap/yap.html#SEC150)
  - [ ] [FASSIL](https://dectau.uclm.es/fasill/)
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

## Specifying knowledge

Pylo allows you to conveniently specify the knowledge base and the query it with different prolog engines.
All basic constructs (constants, variables, functors and predicates) should be created using the `global_context`, which ensures that there are not duplicates. 

```python
from pylo.engines.language import global_context, Literal, Clause, Conj, Structure, List, list_func

# create some constants 
luke = global_context.get_constant("luke")             
anakin = global_context.get_constant("anakin")
leia = global_context.get_constant("leia")
padme = global_context.get_constant("padme")


# create predicates
father = global_context.get_predicate("father", 2)      
mother = global_context.get_predicate("mother", 2)
parent = global_context.get_predicate("parent", 2)


# create literals
f1 = Literal(father, [anakin, luke])                    
f2 = Literal(father, [anakin, leia])
f3 = Literal(mother, [padme, luke])
f4 = Literal(mother, [padme, leia])


# create Variables
X = global_context.get_variable("X")                   
Y = global_context.get_variables("Y")


# create clauses 
head = Literal(parent, [X,Y])                           
body1 = Literal(father, [X,Y])
body2 = Literal(mother, [X,Y])
rule1 = Clause(head, Conj(body1))
rule2 = Clause(head, Conj(body2))


# create structures
sabre = global_context.get_constant("sabre")
green = global_context.get_constant("green")
item = global_context.get_functor("item")

struct = Structure(item, [sabre, green])


# create lists
l = List([padme, leia, 1, 2, 3])
``` 

Such an explicit object-oriented way might be suited for automated construction of programs.
Pylo also provides many convenient shortcuts for less tedious construction of knowledge bases.
The above example could have been constructed in the following way

```python
from pylo.engines.language import global_context, List

# construct predicates
father = global_context.get_predicate("father", 2)
mother = global_context.get_predicate("mother", 2)
parent = global_context.get_predicate("parent", 2)
belongs_to = global_context.get_predicate("belongs_to", 2)

# create facts directly
#    applying the predicate symbol to terms/strings creates a literal
#        it also converts strings to the appropriate structures
f1 = father("anakin", "luke")
f2 = father("anakin", "leia")
f3 = mother("padme", "luke")
f4 = mother("padme", "leia")

# create structures directly
#     applying the functor to a series of terms/strings creates a structure
#     it also knows how to convert strings to the right form
item = global_context.get_functor("item", 2)
struct = item("sabre", "green")

f5 = belongs_to(struct, "luke")


# create list
l = List(["padme", "leia", 1, 2, 3])  # if constants are numbers, just use python data structures


# creating clauses
rule1 = parent("X", "Y") <= father("X", "Y")
rule2 = parent("X", "Y") <= mother("X", "Y")
```

## Querying Prolog

The first step is to create a Prolog instance
```python
from pylo.engines.SWIProlog import SWIProlog
from pylo.engines.XSBProlog import XSBProlog
from pylo.engines.GnuProlog import GNUProlog


# Create GNU Prolog instance
pl_gnu = GNUProlog()

# create XSB Prolog
pl_xsb = XSBProlog("/Users/seb/Documents/programs/XSB")

# create SWI Prolog
pl_swi = SWIProlog('/usr/local/bin/swipl')
```

Two things need to be noted:
 - `SWIProlog` takes the path to the executable as an argument. If the path is standard, i.e. is `/usr/local/bin/swipl` on OSX, no argument needs to be passed
 - `XSBProlog` takes a path to the XSB sources as an argument
 
 
All Prolog engines have a unified interface:
```python
from pylo.engines.Prolog import Prolog
pl = Prolog()

# consult file
pl.consult("metagol.pl")

# load module
# Pylo does not provide a standardization of modules accross different engines
#    this means that it is your job to ensure that the correct mofule nam is provided 
#
#    for instance, GNU prolog does not have modules
#                  XSB Prolog needs to specify which predicates to load frm the library, 
#                               this is provided as an extra names arguments 'predicates', which takes a list of predicates
pl.use_module("library(lists")

# asserta a fact or a clause
pl.asserta()

# assertz a fact or a clause
pl.assertz()


# retract literal
pl.retract()

# check whether it is possible to satisfy a query
# has_solution(...) can take any number of literals as an argument, which is interpreted as a conjunction
pl.has_solution()

# query all solutions
# query(...) takes any number of literals as an input, which is interpreted as a conjuncion
#       it additionally takes 'max_solutions' arguments, which can be used to limit the number of solutions to look for
pl.query()
```


A more elaborate example
```python
from pylo.engines.XSBProlog import XSBProlog
from pylo.engines.language import global_context

pl = XSBProlog("/Users/seb/Documents/programs/XSB")

person = global_context.get_predicate("person", 1)
friends = global_context.get_predicate("friends", 2)
stress = global_context.get_predicate("stress", 1)
influences = global_context.get_predicate("influences", 2)
smokes = global_context.get_predicate("smokes", 1)
asthma = global_context.get_predicate("asthma", 1)

pl.assertz(person("a"))
pl.assertz(person("b"))
pl.assertz(person("c"))
pl.assertz(friends("a", "b"))
pl.assertz(friends("a", "c"))

pl.assertz(stress("X") <= person("X"))
pl.assertz(influences("X", "Y") <= person("X") & person("Y"))
pl.assertz(smokes("X") <= stress("X"))
pl.assertz(smokes("X") <= friends("X", "Y") & influences("Y", "X") & smokes("Y"))
pl.assertz(asthma("X") <= smokes("X"))

query_p = person("X")
tv = pl.query(query_p)
print("all persons: ", tv)

query_f = friends("X", "Y")
tv = pl.query(query_f)
print("all friends: ", tv)

query_st = stress("Y")
tv = pl.query(query_st)
print("all stressed people: ", tv)

tv = pl.query(influences("X", "Y"))
print("all influences: ", tv)

tv = pl.query(smokes("X"))
print("all smokers: ", tv)

tv = pl.query(asthma("X"), max_solutions=3)
print("all asthma: ", tv)
```



# Missing features

 - [ ] remember all created variables, so that they can be properly bound to the objects in the language
 - [ ] providing python functions as predicates
 - [ ] documentation
   - [ ] high-level engine
   - [ ] low-level primitives 