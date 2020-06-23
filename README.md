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
  - [ ] [TauProlog](http://tau-prolog.org/)
  - [ ] [Bousi Prolog](https://dectau.uclm.es/bousi-prolog/)

# Practical

do `export LD_LIBRARY_PATH=/Users/seb/.ciaoroot/master/build/eng/ciaoengine/objs/DARWINx86_64/` before importing python lib

for swipl `export LD_LIBRARY_PATH=/usr/local/Cellar/swi-prolog/8.2.0/libexec/lib/swipl/lib/x86_64-darwin`