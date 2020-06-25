//
// Created by Sebastijan Dumancic on 22/05/2020.
//

#ifndef CIAOPY_LANGUAGE_H
#define CIAOPY_LANGUAGE_H

#include <iostream>
#include <utility>
#include <vector>
using namespace std;


class Term {
protected:
    string name;
public:
    explicit Term(string n);

    virtual ~Term() = default;

    virtual string getName();
};

class Const: public Term {
    using Term::Term;
};

class Integer: public Const {
    using Const::Const;

protected:
    int value;
public:
    explicit Integer(int val);

    [[nodiscard]] int getValue() const;
};

class Decimal: public Const {
    using Const::Const;
protected:
    double value;
public:
    explicit Decimal(double val);

    [[nodiscard]] double getValue() const;
};

class Var: public Term {
    using Term::Term;
};

class Functor {
protected:
    string name;
    int arity;
public:
    Functor(string n, int ar);

    string getName();

    [[nodiscard]] int getArity() const;
};


class Structure: public Term {
protected:
    Functor fun;
    vector<Term*> arguments;
public:
    Structure(Functor f, vector<Term*> args);
    Functor getFunctor();
    vector<Term*> getArguments();
};

class List: public Term {
protected:
    vector<Term*> elements;
public:
    explicit List(vector<Term*> elems);

    vector<Term*> getElements();

    Term getHead();

    List getTail();
};

#endif //CIAOPY_LANGUAGE_H
