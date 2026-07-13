import re
from rply import LexerGenerator

class SemAnalyzer():
    def __init__(self, sym_table):
        self.lexer = LexerGenerator()
        self.sym_table = sym_table 
        self.num_errors = 0

    def verify(self, ast):
        # El nodo raíz debe ser 'programa'
        if ast.etiqueta() == 'programa':
            for instr in ast.hijos() or []:
                self.verifySubTree(instr)
        else:
            print("**ERROR SEMÁNTICO: raíz inválida, se esperaba 'programa'**")
            self.num_errors += 1
        return self.num_errors

    def verifySubTree(self, ast):
        etiqueta = ast.etiqueta()
        hijos = ast.hijos() or []
        # Verificar recursivamente los hijos
        for h in hijos:
            if hasattr(h, 'etiqueta'):
                self.verifySubTree(h)

        # Declaración con asignación
        if etiqueta == 'declara_asigna':
            tipo_decl, id_var, expr = hijos
            tipo_expr = self.tipoSubTree(expr)
            if tipo_decl != tipo_expr:
                print(f"**ERROR SEMÁNTICO: Se esperaba un valor '{tipo_decl}' para la variable {id_var}**")
                self.num_errors += 1
            return

        # Asignación
        if etiqueta == '=':
            id_var, expr = hijos
            if id_var not in self.sym_table:
                print(f"**ERROR SEMÁNTICO: variable '{id_var}' no declarada**")
                self.num_errors += 1
            else:
                tipo_decl = self.sym_table[id_var]
                tipo_expr = self.tipoSubTree(expr)
                if tipo_decl != tipo_expr:
                    print(f"**ERROR SEMÁNTICO: Se esperaba un valor '{tipo_decl}' para la variable {id_var}**")
                    self.num_errors += 1
            return

        

    def tipoSubTree(self, ast):
        # Literales y variables representadas como strings
        if isinstance(ast, str):
            # Literal cadena
            if ast.startswith('"') and ast.endswith('"'):
                return 'cadena'
            # Booleano literal
            if ast in ('Verdadero', 'Falso', 'True', 'False'):
                return 'booleano'
            # Entero literal
            if re.fullmatch(r'-?\d+', ast):
                return 'entero'
            # Real literal
            if re.fullmatch(r'-?\d*\.\d+', ast):
                return 'real'
            # Variable
            if ast in self.sym_table:
                return self.sym_table[ast]
            # Desconocido: no emitir mensaje para literales inválidos
            return None

        # Literales como tipos nativos
        if isinstance(ast, int):
            return 'entero'
        if isinstance(ast, float):
            return 'real'
        if isinstance(ast, bool):
            return 'booleano'

        # Nodos compuestos (operadores)
        etiqueta = ast.etiqueta()
        hijos = ast.hijos() or []

        # Operadores aritméticos
        if etiqueta in ('+', '-', '*', '/') and len(hijos) == 2:
            t1 = self.tipoSubTree(hijos[0])
            t2 = self.tipoSubTree(hijos[1])
            if t1 not in ('entero', 'real') or t2 not in ('entero', 'real'):
                self.num_errors += 1
                return None
            return 'real' if 'real' in (t1, t2) else 'entero'

        # Comparaciones
        if etiqueta in ('==', '!=', '<', '>', '<=', '>=') and len(hijos) == 2:
            # Asumimos comparaciones válidas para tipos iguales
            return 'booleano'

        # Operadores lógicos
        if etiqueta in ('y', 'o') and len(hijos) == 2:
            return 'booleano'
        if etiqueta == 'no' and len(hijos) == 1:
            return 'booleano'

        # Nodo no reconocido
        return None
