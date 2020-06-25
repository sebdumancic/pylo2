//
// Created by Sebastijan Dumancic on 22/05/2020.
//

#include "language.h"

#include <utility>

Term::Term(string n): name(std::move(n)) {

}

string Term::getName() {
    return name;
}

Functor::Functor(string n, int ar): name(std::move(n)), arity(ar) {

}

string Functor::getName() {
    return name;
}

int Functor::getArity() const {
    return arity;
}

Structure::Structure(Functor f, vector<Term*> args) : Term(f.getName()), fun(std::move(f)), arguments(std::move(args)) {

}

Functor Structure::getFunctor() {
    return fun;
}

vector<Term*> Structure::getArguments() {
    return arguments;
}

Integer::Integer(int val): value(val), Const(to_string(val)) {

}

int Integer::getValue() const {
    return value;
}

Decimal::Decimal(double val): value(val), Const(to_string(val)) {

}

double Decimal::getValue() const {
    return value;
}

List::List(vector<Term*> elems): elements(std::move(elems)), Term("cons") {
}

vector<Term*> List::getElements() {
    return elements;
}

Term List::getHead() {
   return reinterpret_cast<const Term &>(elements[0]);
}

List List::getTail() {
    vector<Term*> elems = vector<Term*>(elements.begin() + 1, elements.end());
    List lr(elems);
    return lr;
}
