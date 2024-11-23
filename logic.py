from sympy import sympify, symbols, And, Not

from sympy.logic.boolalg import to_cnf, And, Or, Equivalent

class KB:
    """A knowledge base to which you can tell and ask sentences.
    To create a KB, first subclass this class and implement
    tell, ask_generator, and retract. Why ask_generator instead of ask?
    The book is a bit vague on what ask means --
    For a Propositional Logic KB, ask(P & Q) returns True or False, but for an
    FOL KB, something like ask(Brother(x, y)) might return many substitutions
    such as {x: Cain, y: Abel}, {x: Abel, y: Cain}, {x: George, y: Jeb}, etc.
    So ask_generator generates these one at a time, and ask either returns the
    first one or returns False."""

    def __init__(self, sentence=None):
        if sentence:
            self.tell(sentence)

    def tell(self, sentence):
        """Add the sentence to the KB."""
        raise NotImplementedError

    def ask(self, query):
        """Return a substitution that makes the query true, or, failing that, return False."""
        return first(self.ask_generator(query), default=False)

    def ask_generator(self, query):
        """Yield all the substitutions that make query true."""
        raise NotImplementedError

    def retract(self, sentence):
        """Remove sentence from the KB."""
        raise NotImplementedError


class PropKB(KB):
    """A KB for propositional logic. Inefficient, with no indexing."""

    def __init__(self, sentence=None):
        super().__init__(sentence)
        self.clauses = []

    def tell(self, sentence):
        """Add the sentence's clauses to the KB."""
        self.clauses.extend(conjuncts(to_cnf(sentence)))

    def ask_generator(self, query):
        """Yield the empty substitution {} if KB entails query; else no results."""
        if pl_resolution(self, query):
            yield {}

    def ask_if_true(self, query):
        """Return True if the KB entails query, else return False."""
        for _ in self.ask_generator(query):
            return True
        return False

    def retract(self, sentence):
        """Remove the sentence's clauses from the KB."""
        for c in conjuncts(to_cnf(sentence)):
            if c in self.clauses:
                self.clauses.remove(c)


# ______________________________________________________________________________


def pl_resolution(kb, alpha):
    """
    Propositional-logic resolution: say if alpha follows from KB.
    >>> pl_resolution(horn_clauses_KB, A)
    True
    """
    clauses = kb.clauses + conjuncts(to_cnf(~alpha))
    new = set()
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i + 1, n)]
        for (ci, cj) in pairs:
            resolvents = pl_resolve(ci, cj)
            if False in resolvents:
                return True
            new = new.union(set(resolvents))
        if new.issubset(set(clauses)):
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)


def pl_resolve(ci, cj):
    """Return all clauses that can be obtained by resolving clauses ci and cj."""
    clauses = []
    for di in disjuncts(ci):
        for dj in disjuncts(cj):
            if di == ~dj or ~di == dj:
                clauses.append(associate(Or, unique(remove_all(di, disjuncts(ci)) + remove_all(dj, disjuncts(cj)))))
    return clauses

# ______________________________________________________________________________

def associate(op, args):
    """Given an associative op, return an expression with the same
    meaning as Expr(op, *args), but flattened -- that is, with nested
    instances of the same op promoted to the top level.
    >>> associate('&', [(A&B),(B|C),(B&C)])
    (A & B & C & (B | C))
    >>> associate('|', [A|(B|(C|(A&B)))])
    (A | B | C | (A & B))
    """
    args = dissociate(op, args)
    if len(args) == 0:
        return _op_identity[op]
    elif len(args) == 1:
        return args[0]
    else:
        return op(*args)

_op_identity = {And: True, Or: False}

def dissociate(op, args):
    """Given an associative op, return a flattened list result such
    that Expr(op, *result) means the same as Expr(op, *args).
    >>> dissociate('&', [A & B])
    [A, B]
    """
    result = []

    def collect(subargs):
        for arg in subargs:
            if isinstance(arg, op):
                collect(arg.args)
            else:
                result.append(arg)

    collect(args)
    return result

def conjuncts(expr):
    """Return a list of the conjuncts in the sentence s.
    >>> conjuncts(A & B)
    [A, B]
    >>> conjuncts(A | B)
    [(A | B)]
    """
    return dissociate(And, [expr])

def disjuncts(expr):
    """Return a list of the disjuncts in the sentence s.
    >>> disjuncts(A | B)
    [A, B]
    >>> disjuncts(A & B)
    [(A & B)]
    """
    return dissociate(Or, [expr])


# ______________________________________________________________________________
# Utils

def first(iterable, default=None):
    """Return the first element of an iterable; or default."""
    return next(iter(iterable), default)

def unique(seq):
    """Remove duplicate elements from seq. Assumes hashable elements."""
    return list(set(seq))

def remove_all(item, seq):
    """Return a copy of seq (or string) with all occurrences of item removed."""
    if isinstance(seq, str):
        return seq.replace(item, '')
    elif isinstance(seq, set):
        rest = seq.copy()
        rest.remove(item)
        return rest
    else:
        return [x for x in seq if x != item]


# ______________________________________________________________________________
# Pruebas

if __name__ == '__main__':
    # Prueba 1 - Base de conocimiento del mundo de Wumpus
    # ---------------------------------------------------
    wumpus_kb = PropKB()
    P11, P12, P21, P22, P31, B11, B21 = symbols('P11 P12 P21 P22 P31 B11 B21')

    wumpus_kb.tell(~P11)
    wumpus_kb.tell(Equivalent(B11, (P12 | P21)))
    wumpus_kb.tell(Equivalent(B21, (P11 | P22 | P31)))
    wumpus_kb.tell(~B11)
    wumpus_kb.tell(B21)

    # Descomentar el codigo para ver las soluciones respectivas
    # for i in wumpus_kb.clauses:
    #     print(i)
    
    # print(f"\n{pl_resolution(wumpus_kb, ~P11), pl_resolution(wumpus_kb, P11)}")
    # print(f"\n{pl_resolution(wumpus_kb, ~P22), pl_resolution(wumpus_kb, P22)}")
    
    
    # Prueba 2 - Problema de dopaje
    # ----------------------------------
    baseConocimiento = PropKB()
    Da, Db, Dc, A, B, C = symbols("Da Db Dc A B C")
    
    # baseConocimiento.tell(Equivalent(Da, (B | C) & ~(B & C)))
    # baseConocimiento.tell(Equivalent(Db, (A | C) & ~(A & C)))
    # baseConocimiento.tell(Equivalent(Dc, (A | B) & ~(A & B)))
    # baseConocimiento.tell((~Da & Db & Dc) | (Da & ~Db & Dc) | (Da & Db & ~Dc))
    
    dijoAlice =(B | C) & ~(B & C)
    dijoBob = (A | C) & ~(A & C)
    dijoCharlie = (A | B) & ~(A & B)
    
    baseConocimiento.tell(dijoAlice)
    baseConocimiento.tell(dijoBob)
    baseConocimiento.tell(dijoCharlie)
    baseConocimiento.tell(A)
    
    for i in baseConocimiento.clauses:
        print(i)
    
    print()
    print(pl_resolution(baseConocimiento, ~A))
    # print(pl_resolution(baseConocimiento, ~B))
    # print(pl_resolution(baseConocimiento, C))
    
    # print(pl_resolution(baseConocimiento, B))
    # print(pl_resolution(baseConocimiento, C))
    
    
    
    # Prueba 3 - Problema con Q
    # ----------------------------------
    # prueba3 = PropKB()
    # Q = symbols("Q")
    
    # prueba3.tell(Q)
    
    # # print(prueba3.clauses)
    # print(sympify("Q"))
    