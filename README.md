`pylo` is a Python front-end for several logic programming engines.
This includes several Prolog engines, but also different flavours of logic programming such as relational programming (kanren) and Datalog.
It allows you to write your program once and execute it with different engines simply by switching the back-end.


**Supported OS:** The library was tested on Linux (Ubuntu) and OSX.

# Supported engines

## Prolog engines

Currently supported:
 - [SWIPL](https://www.swi-prolog.org/)
 - [GNU Prolog](http://www.gprolog.org) (works only on OSX so far; GNU PROLOG's foreign function interface does not compile properly on Linux)
 - [XSB Prolog](http://xsb.sourceforge.net/) 
 
Under development:
 - [ ] [ECLiPSe](http://eclipseclp.org/) and its [Python interface](http://pyclp.sourceforge.net/)
 - [ ] [Ciao Prolog](https://ciao-lang.org/) and its [C interface](https://ciao-lang.org/ciao/build/doc/ciao.html/foreign_interface_doc.html)
 - [ ] [TauProlog](http://tau-prolog.org/)  (with [pyv8](https://code.google.com/archive/p/pyv8/)) 
 
Maybe supported in the future:
  - [ ] [B-Prolog](http://www.picat-lang.org/bprolog) and [C interface](http://www.picat-lang.org/bprolog/download/manual.pdf)
  - [ ] [YAP](http://cracs.fc.up.pt/~nf/Docs/Yap/yap.html) and [C interface](http://cracs.fc.up.pt/~nf/Docs/Yap/yap.html#SEC150)
  - [ ] [FASSIL](https://dectau.uclm.es/fasill/)
  - [ ] [Bousi Prolog](https://dectau.uclm.es/bousi-prolog/)
  
## Datalog engines

A subset of Prolog without functors/structures

Currently supported:
 - [muZ (Z3's datalog engine)](http://www.cs.tau.ac.il/~msagiv/courses/asv/z3py/fixedpoints-examples.htm)
 
Considering:
 - [pyDatalog](https://sites.google.com/site/pydatalog/home)


## Relational programming engines

Prolog without side-effects (cut and so on)

Currently supported:
 - [miniKanren](https://github.com/pythological/kanren); seems to be actively maintained
 

## Deductive database engines

Currently supported:
 - none yet
 
Considering:
 - [Grakn](https://grakn.ai/)
 
 
## Answer set programming

Currently supported:
  - none yet
  
Considering:
   - [aspirin](https://github.com/potassco/asprin)
   - [clorm](https://github.com/potassco/clorm)
   - [asp-lite](https://github.com/lorenzleutgeb/asp-lite)
   - [hexlite](https://github.com/hexhex/hexlite)
   - [clyngor](https://github.com/aluriak/clyngor)





# Installation

## Installation with pip

**STEP 1:** install you favourite Prolog engine(s). Make sure they are available through the terminal. `pylo` relies on the `which` command to identify the right paths.

**STEP 2:** clone this repository

**STEP 3:** install with pip
```shell script
pip install -v .
```

**STEP 4 (optional):** Test
```python
from pylo.tests import all_swipl_tests, all_gnu_tests, all_xsb_tests, test_kanren, test_datalog

all_swipl_tests()
all_gnu_tests()
all_xsb_tests("[path_to_XSB_folder]")  # the same folder for installation
test_kanren()
test_datalog()
```

If something goes wrong, refer to the [INSTALL.md](INSTALL.md) file for the alternative procedures.


## Other practical considerations

 - if you are using zsh shell instead of bash, XSB will not be automatically detectable. You will have to manually set the right environmental variable pointing to the location of XSB sources, as described in [INSTALL.md](INSTALL.md).

 - In order to use SWIPL, you need to provide a path to the dynamic library using the `LD_LIBRARY_PATH` env var. For instance, on OSX 
 ```shell script
    export LD_LIBRARY_PATH=/usr/local/Cellar/swi-prolog/8.2.0/libexec/lib/swipl/lib/x86_64-darwin
```
 - For Ciao prolog, you also need to be able to find the dynamic library. On OSX
```shell script
    export LD_LIBRARY_PATH=/Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64/
```
 - Z3Py scripts stored in arbitrary directories can be executed if the 'build/python' directory is added to the PYTHONPATH environment variable and the 'build' directory is added to the DYLD_LIBRARY_PATH environment variable.


# Usage

## Language design

`pylo` follows the logic programming terminology, instead of Prolog terminology,
The basic constructs include terms:
 - constants: `luke, leia, anakin` or Python numbers like `1, -3, 3.14`
 - variables: `X, Y`
 - structures: `sabre(green,long), date(2020,january,1)`
 - lists (a special kind of structure): `List([1,2,3,4,5])`
 
To construct clauses, one needs:
 - predicates: `parent, ...`
 - literals:
   - atoms (predicate applied to terms): `parent(vader,luke), mother(padme, leia)`
   - negations of atoms: `Not(parent(vader,luke))`
 - clauses: `parent(X,Y) :- mother(X,Y)`
 
 
To reduce the memory usage, constants, variables, functors and predicates should be constructed through context:
 - constants: `c_const('luke')` creates a constant `luke` (for numbers, just use Python structures)
 - variables: `c_var('X')` creates a variables `X`
 - predicates: `c_pred('parent', 2)` creates a predicate `parent` with arity 2
 - functors: `c_functor('date', 3)` creates a functor `date` with arity 3
 
If you want to use a proposition in a clause (a functor without arguments), like `a :- ...`, create it as a `Predicate` with arity 0. 
Be careful to construct clauses with literals, not structures.
 
 


## Specifying knowledge

Pylo allows you to conveniently specify the knowledge base and the query it with different prolog engines.
All basic constructs (constants, variables, functors and predicates) should be created using the *global context* (functions prefixed with `c_`: `c_const`, `c_pred`, `c_var`, `c_functor`), which ensures that there are not duplicates. 

```python
from pylo.language.lp import c_pred, c_var, c_const, c_functor, Atom, Clause, Body, Structure, List

# create some constants 
luke = c_const("luke")             
anakin = c_const("anakin")
leia = c_const("leia")
padme = c_const("padme")


# create predicates
father = c_pred("father", 2)      
mother = c_pred("mother", 2)
parent = c_pred("parent", 2)


# create literals
f1 = Atom(father, [anakin, luke])                    
f2 = Atom(father, [anakin, leia])
f3 = Atom(mother, [padme, luke])
f4 = Atom(mother, [padme, leia])


# create Variables
X = c_var("X")                   
Y = c_var("Y")


# create clauses 
head = Atom(parent, [X,Y])                           
body1 = Atom(father, [X,Y])
body2 = Atom(mother, [X,Y])
rule1 = Clause(head, Body(body1))
rule2 = Clause(head, Body(body2))


# create structures
sabre = c_const("sabre")
green = c_const("green")
item = c_functor("item")

struct = Structure(item, [sabre, green])


# create lists
l = List([padme, leia, 1, 2, 3])
``` 

Such an explicit object-oriented way might be suited for automated construction of programs.
Pylo also provides many convenient shortcuts for less tedious construction of knowledge bases.
The above example could have been constructed in the following way

```python
from pylo.language.lp import c_pred, c_const, c_var, c_functor, List

# construct predicates
father = c_pred("father", 2)
mother = c_pred("mother", 2)
parent = c_pred("parent", 2)
belongs_to = c_pred("belongs_to", 2)

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
item = c_functor("item", 2)
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
from pylo.engines.prolog import SWIProlog
from pylo.engines.prolog import XSBProlog
from pylo.engines.prolog import GNUProlog


# Create GNU Prolog instance
pl_gnu = GNUProlog()

# create XSB Prolog
# you need to provide the path
pl_xsb = XSBProlog("[path to the XSB folder used in installation]")

# create SWI Prolog
# the path to SWIPL binary is optional if it corresponds
pl_swi = SWIProlog('/usr/local/bin/swipl') 

# create datalog instance
from pylo.engines.datalog import MuZ
solver_data = MuZ()

# create kanren instance
from pylo.engines.kanren import MiniKanren
solver_kan = MiniKanren()
```

Two things need to be noted:
 - `SWIProlog` takes the path to the executable as an argument. If the path is standard, i.e. is `/usr/local/bin/swipl` on OSX, no argument needs to be passed
 - `XSBProlog` takes a path to the XSB sources as an argument
 
 
All Prolog engines have a unified interface:
```python
from pylo.engines.prolog import Prolog
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
pl.use_module("library(lists)")

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
from pylo.engines.prolog import XSBProlog
from pylo.language.lp import c_pred 

pl = XSBProlog("/Users/seb/Documents/programs/XSB")

person = c_pred("person", 1)
friends = c_pred("friends", 2)
stress = c_pred("stress", 1)
influences = c_pred("influences", 2)
smokes = c_pred("smokes", 1)
asthma = c_pred("asthma", 1)

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

 - [ ] providing python functions as predicates
 - [ ] support for pairs (`[|]/2` or `./2`)
