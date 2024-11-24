from sympy import sympify, symbols, And, Not

from sympy.logic.boolalg import to_cnf, And, Or, Equivalent

class KB:
    """
    Base de Conocimiento (Knowledge Base, KB) para almacenar y consultar conocimiento lógico.
    Esta clase actúa como base para construir sistemas lógicos más específicos.
    
    Métodos que deben implementarse en subclases:
    - `tell`: Añadir sentencias a la base de conocimiento.
    - `ask_generator`: Generar sustituciones que hacen verdadera una consulta.
    - `retract`: Eliminar sentencias de la base de conocimiento.
    """

    def __init__(self, sentence=None):
        """
        Inicializa la base de conocimiento con una sentencia
        """
        if sentence:
            self.tell(sentence)

    def tell(self, sentence):
        """
        Anñade una sentencia a la base de conocimiento
        """
        raise NotImplementedError

    def ask(self, query):
        """
        Consulta la base de conocimeinto para verificar si una consulta es
        verdadera. Retorna la primera sustitución encontrada que hace
        verdadera la consulta o falsa.
        """
        return first(self.ask_generator(query), default=False)

    def ask_generator(self, query):
        """
        Generador que devuelve todas las sustituciones que hacen verdadera
        la consulta.
        """
        raise NotImplementedError

    def retract(self, sentence):
        """
        Remueve una sentencia de la base de conocimiento
        """
        raise NotImplementedError


class PropKB(KB):
    """
    Base de conocimiento de lógica proposicional.
    """

    def __init__(self, sentence=None):
        """
        Inicializa la base de conocimiento y opcionalmente añade una sentencia.
        """
        super().__init__(sentence)
        self.clauses = []

    def tell(self, sentence):
        """
        Convierte una sentencia a forma normal conjuntiva (CNF) y añade sus
        cláusulas a la base.
        """
        self.clauses.extend(conjuncts(to_cnf(sentence)))

    def ask_generator(self, query):
        """
        Generador que produce sustituciones si la base de conocimiento
        implica la consulta.
        """
        if pl_resolution(self, query):
            yield {}

    def ask_if_true(self, query):
        """
        Consulta si la base de conocimiento implica la consulta. Retorna
        verdadero si es implicada, caso contrario retorna falso.
        """
        for _ in self.ask_generator(query):
            return True
        return False

    def retract(self, sentence):
        """
        Remueve las cláusulas de una sentencia de la base de conocimiento.
        """
        for c in conjuncts(to_cnf(sentence)):
            if c in self.clauses:
                self.clauses.remove(c)


# ______________________________________________________________________________


def pl_resolution(kb, alpha):
    """
    Algoritmo de resolución para lógica proposicional. Verifica si una 
    consulta alpha es implicada por la base de conocimiento kb
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
    """
    Realiza la resolución entre dos cláusulas ci y cj. Retorna todas
    las cláusulas derivadas al resolverlas.
    """
    clauses = []
    for di in disjuncts(ci):
        for dj in disjuncts(cj):
            if di == ~dj or ~di == dj:
                clauses.append(associate(Or, unique(remove_all(di, disjuncts(ci)) + remove_all(dj, disjuncts(cj)))))
    return clauses

# ______________________________________________________________________________

def associate(op, args):
    """
    simplifica expresiones al asociar operaciones lógicas del mismo tipo.
    Combina argumentos anidados en una estructura plana.
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
    """
    Descompone expresiones lógicas en lsitas planas de argumentos.
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
    """Retorna una lista de los conjuntos en una expresion lógica.
    >>> conjuncts(A & B)
    [A, B]
    >>> conjuncts(A | B)
    [(A | B)]
    """
    return dissociate(And, [expr])

def disjuncts(expr):
    """Retorna una lista de los disjuntos en una expresión lógica.
    >>> disjuncts(A | B)
    [A, B]
    >>> disjuncts(A & B)
    [(A & B)]
    """
    return dissociate(Or, [expr])


# ______________________________________________________________________________
# Utils

def first(iterable, default=None):
    """
    Retorna el primer elemento de un iterable o un valor predeterminado.
    """
    return next(iter(iterable), default)

def unique(seq):
    """
    Elimina elementos duplicados de una secuencia, asumiendo que son 'hasheables'.
    """
    return list(set(seq))

def remove_all(item, seq):
    """
    Retorna una copia de una secuencia o cadena con todas las ocurrencias de un ítem eliminadas.
    """
    if isinstance(seq, str):
        return seq.replace(item, '')
    elif isinstance(seq, set):
        rest = seq.copy()
        rest.remove(item)
        return rest
    else:
        return [x for x in seq if x != item]
