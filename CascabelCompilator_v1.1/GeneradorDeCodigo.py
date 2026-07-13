

from Arbol import Arbol
import re

class CodeGenerator:

    BOOLEAN_LITERALS = {
        "Verdadero": "True",
        "verdadero": "True",
        "True": "True",
        "true": "True",
        "Falso": "False",
        "falso": "False",
        "False": "False",
        "false": "False",
    }

    def __init__(self, symbols):
        self.output = open("out.py", "w")
        self.indent = 0
        self.symbols = symbols

    def generate(self, ast):
        # Si es lista de nodos, los generamos en orden
        if isinstance(ast, list):
            for node in ast:
                self.generate(node)
            return

        # Hoja: puede ser literal (número, cadena, bool) o nombre de variable
        if isinstance(ast, str):
            # Cadena con variables $var
            if "$" in ast and ast.startswith('"') and ast.endswith('"'):
                self.output.write(self._string_to_code(ast))
                return
            # Literal booleano
            if ast in self.BOOLEAN_LITERALS:
                self.output.write(self.BOOLEAN_LITERALS[ast])
                return
            # Literal numérico (ENTERO o REAL)
            if re.fullmatch(r"\d+(\.\d+)?", ast):
                self.output.write(ast)
                return
            # Cadena literal simple (p.ej. '"hola"')
            if ast.startswith('"') and ast.endswith('"'):
                self.output.write(ast)
                return
            # Identificador (variable)
            self.output.write(ast)
            return

        # Hoja numérica o booleano ya convertido
        if isinstance(ast, (int, float, bool)):
            self.output.write(str(ast))
            return

        tag = ast.etiqueta()
        hijos = ast.hijos() or []
        indent = "    " * self.indent

        # ---------------------------------------------------
        # Raíz programa
        # ---------------------------------------------------
        if tag == "programa":
            for instr in hijos:
                self.generate(instr)
            return

        # ---------------------------------------------------
        # Declaraciones
        # ---------------------------------------------------
        if tag == "declara":
            tipo, var = hijos
            defaults = {
                "entero": "0",
                "real":   "0.0",
                "cadena": '""',
                "booleano": "False"
            }
            self.output.write(f"{indent}{var} = {defaults[tipo]}\n")
            return

        if tag == "declara_asigna":
            tipo, var, expr = hijos
            self.output.write(f"{indent}{var} = ")
            self._gen_expr(expr)
            self.output.write("\n")
            return

        # ---------------------------------------------------
        # Asignación
        # ---------------------------------------------------
        if tag == "=":
            var, expr = hijos
            self.output.write(f"{indent}{var} = ")
            self._gen_expr(expr)
            self.output.write("\n")
            return

        # ---------------------------------------------------
        # Lectura (lee)
        # ---------------------------------------------------
        if tag == "lee":
            var = hijos[0]
            tipo = self.symbols.get(var, "cadena")
            if tipo == "entero":
                self.output.write(f"{indent}{var} = int(input())\n")
            elif tipo == "real":
                self.output.write(f"{indent}{var} = float(input())\n")
            elif tipo == "booleano":
                self.output.write(
                    f"{indent}{var} = input().lower() in ('verdadero','true')\n")
            else:
                self.output.write(f"{indent}{var} = input()\n")
            return

        # ---------------------------------------------------
        # Escritura (escribe)
        # ---------------------------------------------------
        if tag == "escribe":
            expr = hijos[0]
            self.output.write(f"{indent}print(")
            self._gen_expr(expr)
            self.output.write(")\n")
            return

        # ---------------------------------------------------
        # If sin else
        # ---------------------------------------------------
        if tag == "si":
            # hijos puede ser [cond, instr1, instr2, ...] o [cond, [instr1, instr2, ...]]
            cond = hijos[0]
            then_blk = (
                hijos[1]
                if isinstance(hijos[1], list)
                else hijos[1:]
            )
            self.output.write(f"{indent}if ")
            self._gen_expr(cond)
            self.output.write(":\n")
            self.indent += 1
            for instr in then_blk:
                self.generate(instr)
            self.indent -= 1
            return

        # ---------------------------------------------------
        # If con else
        # ---------------------------------------------------
        if tag == "si_sino":
            cond, then_blk, else_blk = hijos
            self.output.write(f"{indent}if ")
            self._gen_expr(cond)
            self.output.write(":\n")
            self.indent += 1
            for instr in then_blk:
                self.generate(instr)
            self.indent -= 1
            self.output.write(f"{indent}else:\n")
            self.indent += 1
            for instr in else_blk:
                self.generate(instr)
            self.indent -= 1
            return

        # ---------------------------------------------------
        # While
        # ---------------------------------------------------
        if tag == "mientras":
            cond, body = hijos
            self.output.write(f"{indent}while ")
            self._gen_expr(cond)
            self.output.write(":\n")
            self.indent += 1
            loop_list = body if isinstance(body, list) else [body]
            for instr in loop_list:
                self.generate(instr)
            self.indent -= 1
            return

        # ---------------------------------------------------
        # For
        # ---------------------------------------------------
        if tag == "para":
            var, inicio, fin, body = hijos
            self.output.write(f"{indent}for {var} in range(")
            self._gen_expr(inicio)
            self.output.write(", ")
            self._gen_expr(fin)
            self.output.write(" + 1):\n")
            self.indent += 1
            loop_list = body if isinstance(body, list) else [body]
            for instr in loop_list:
                self.generate(instr)
            self.indent -= 1
            return

        # ---------------------------------------------------
        # Fallback: tratarlo como expresión
        # ---------------------------------------------------
        self._gen_expr(ast)

    def _gen_expr(self, expr):
        # Literales y nombres
        if isinstance(expr, str):
            # dinámico con $var
            if "$" in expr and expr.startswith('"') and expr.endswith('"'):
                self.output.write(self._string_to_code(expr))
                return
            # booleano
            if expr in self.BOOLEAN_LITERALS:
                self.output.write(self.BOOLEAN_LITERALS[expr])
                return
            # numérico
            if re.fullmatch(r"\d+(\.\d+)?", expr):
                self.output.write(expr)
                return
            # cadena literal
            if expr.startswith('"') and expr.endswith('"'):
                self.output.write(expr)
                return
            # identificador
            self.output.write(expr)
            return

        if isinstance(expr, (int, float, bool)):
            self.output.write(str(expr))
            return

        tag = expr.etiqueta()
        hijos = expr.hijos() or []

        # NOT unario
        if tag == "no":
            self.output.write("(not ")
            self._gen_expr(hijos[0])
            self.output.write(")")
            return

        # Signo negativo unario
        if tag == "negativo":
            self.output.write("(-")
            self._gen_expr(hijos[0])
            self.output.write(")")
            return

        # Aritméticos
        if tag in ("+", "-", "*", "/"):
            a, b = hijos
            self.output.write("(")
            self._gen_expr(a)
            self.output.write(f" {tag} ")
            self._gen_expr(b)
            self.output.write(")")
            return

        # Comparaciones
        if tag in ("==", "!=", "<", ">", "<=", ">="):
            a, b = hijos
            self.output.write("(")
            self._gen_expr(a)
            self.output.write(f" {tag} ")
            self._gen_expr(b)
            self.output.write(")")
            return

        # Booleanos
        if tag in ("o", "y"):
            a, b = hijos
            op_py = " or " if tag == "o" else " and "
            self.output.write("(")
            self._gen_expr(a)
            self.output.write(op_py)
            self._gen_expr(b)
            self.output.write(")")
            return

        # Fallback: recorrer hijos
        for child in hijos:
            self._gen_expr(child)

    def _string_to_code(self, s):
        # Recibe algo como '"texto $var más texto"'
        # Le quitamos las comillas exteriores y partimos
        inner = s[1:-1]
        parts = re.split(r"(\$[A-Za-z_][A-Za-z0-9_]*)", inner)
        code_parts = []
        for p in parts:
            if not p:
                continue
            if p.startswith("$"):
                code_parts.append(f"str({p[1:]})")
            else:
                code_parts.append(repr(p))
        return " + ".join(code_parts)

    def close(self):
        self.output.close()
