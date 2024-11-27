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

if __name__ == '__main__':

    #Problema 1
    # Definir símbolos
    A, B, C = symbols("A B C")  # A: Alice tomó drogas, B: Bob, C: Charlie

    # Declaraciones de los sospechosos
    dijoAlice = (B | C) & ~(B & C)  # Bob o Charlie, pero no ambos
    dijoBob = (A | C) & ~(A & C)    # Ali   ce o Charlie, pero no ambos
    dijoCharlie = (A | B) & ~(A & B)  # Alice o Bob, pero no ambos

    # Crear Base de Conocimiento
    baseConocimiento = PropKB()
    baseConocimiento.tell(dijoAlice)
    baseConocimiento.tell(dijoCharlie)
    baseConocimiento.tell(C) #Se dice que Charlie esta dopado, reduce incertidumbre

    print("Cláusulas en la Base de Conocimiento:")
    for clause in baseConocimiento.clauses:
        print(clause)

    # Verificar quién es culpable
    print("¿Alice es culpable?", pl_resolution(baseConocimiento, A))  # Resolución para A
    print("¿Bob es culpable?", pl_resolution(baseConocimiento, B))    # Resolución para B
    print("¿Charlie es culpable?", pl_resolution(baseConocimiento, C))  # Resolución para C

    print("---------------------------------\nProblema 2\n")
    
    #Problema 2
    M, I, Ma, H, Mg = symbols("M I Ma H Mg")  # M: mítico, I: inmortal, Ma: mamífero, H: cuernos, Mg: mágico

    # Declaraciones
    regla1 = M>>I           # Si es mítico, entonces es inmortal
    regla2 = ~M >> (Ma & ~I)      # Si no es mítico, entonces es mamífero
    regla3 = (I | Ma) >> H    # Si es inmortal o mamífero, entonces tiene cuernos
    regla4 = H >> Mg           # Si tiene cuernos, entonces es mágico

    # Crear Base de Conocimiento
    baseConocimiento = PropKB()
    baseConocimiento.tell(regla1)
    baseConocimiento.tell(regla2)
    baseConocimiento.tell(regla3)
    baseConocimiento.tell(regla4)
    baseConocimiento.tell(M)

    print("Cláusulas en la Base de Conocimiento:")

    print("Caso 1: Unicornio es mítico")
    for clause in baseConocimiento.clauses:
        print(clause)

    # Preguntas
    print("¿El unicornio es mítico?", pl_resolution(baseConocimiento, M))
    print("¿El unicornio es mágico?", pl_resolution(baseConocimiento, Mg))
    print("¿El unicornio tiene cuernos?", pl_resolution(baseConocimiento, H))
    print("¿El unicornio es inmortal?", pl_resolution(baseConocimiento, I))
    print("¿El unicornio es un mamífero?", pl_resolution(baseConocimiento, Ma))

    print("\nCaso 2: Unicornio no es mítico")

    baseConocimiento.retract(M)
    baseConocimiento.tell(~M)
    print("¿El unicornio es mítico?", pl_resolution(baseConocimiento, M))
    print("¿El unicornio es mágico?", pl_resolution(baseConocimiento, Mg))
    print("¿El unicornio tiene cuernos?", pl_resolution(baseConocimiento, H))
    print("¿El unicornio es inmortal?", pl_resolution(baseConocimiento, I))
    print("¿El unicornio es un mamífero?", pl_resolution(baseConocimiento, Ma))