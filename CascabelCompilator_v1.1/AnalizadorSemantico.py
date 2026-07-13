import re


class SemAnalyzer:
    """Comprueba tipos, declaraciones y condiciones en el AST de Cascabel."""

    TIPOS_NUMERICOS = {"entero", "real"}

    LITERALES_BOOLEANOS = {
        "Verdadero",
        "Falso",
        "verdadero",
        "falso",
        "True",
        "False",
        "true",
        "false",
    }

    def __init__(self, sym_table):
        self.sym_table = sym_table
        self.num_errors = 0

    def verify(self, ast):
        """Verifica todo el programa y devuelve el total de errores."""

        self.num_errors = 0

        if ast is None or ast.etiqueta() != "programa":
            self._error("raíz inválida; se esperaba 'programa'")
            return self.num_errors

        self._verify_block(ast.hijos())

        return self.num_errors

    def _error(self, mensaje):
        """Muestra un error y aumenta el contador."""

        print(f"**ERROR SEMÁNTICO: {mensaje}**")
        self.num_errors += 1

    def _verify_block(self, instrucciones):
        """Recorre una instrucción o una lista de instrucciones."""

        if instrucciones is None:
            return

        if isinstance(instrucciones, list):
            for instruccion in instrucciones:
                self.verifySubTree(instruccion)

            return

        self.verifySubTree(instrucciones)

    def _verify_condition(self, condicion, estructura):
        """Comprueba que una condición sea booleana."""

        tipo_condicion = self.tipoSubTree(condicion)

        # Si tipoSubTree ya encontró un error, evitamos generar otro
        # error adicional como consecuencia del primero.
        if tipo_condicion is None:
            return

        if tipo_condicion != "booleano":
            self._error(
                f"la condición de '{estructura}' debe ser booleana, "
                f"pero se obtuvo '{tipo_condicion}'"
            )

    def verifySubTree(self, ast):
        """Verifica una instrucción del árbol."""

        if ast is None:
            return

        if isinstance(ast, list):
            self._verify_block(ast)
            return

        if not hasattr(ast, "etiqueta"):
            return

        etiqueta = ast.etiqueta()
        hijos = ast.hijos() or []

        # Declaración sin asignación:
        # entero numero;
        if etiqueta == "declara":
            return

        # Declaración con asignación:
        # entero numero = 5;
        if etiqueta == "declara_asigna":
            tipo_declarado, id_var, expresion = hijos
            tipo_expresion = self.tipoSubTree(expresion)

            if (
                tipo_expresion is not None
                and tipo_declarado != tipo_expresion
            ):
                self._error(
                    f"se esperaba un valor '{tipo_declarado}' "
                    f"para la variable '{id_var}', pero se obtuvo "
                    f"'{tipo_expresion}'"
                )

            return

        # Asignación:
        # numero = 10;
        if etiqueta == "=":
            id_var, expresion = hijos
            tipo_expresion = self.tipoSubTree(expresion)

            if id_var not in self.sym_table:
                self._error(f"variable '{id_var}' no declarada")
                return

            tipo_declarado = self.sym_table[id_var]

            if (
                tipo_expresion is not None
                and tipo_declarado != tipo_expresion
            ):
                self._error(
                    f"se esperaba un valor '{tipo_declarado}' "
                    f"para la variable '{id_var}', pero se obtuvo "
                    f"'{tipo_expresion}'"
                )

            return

        # Lectura:
        # lee numero;
        if etiqueta == "lee":
            id_var = hijos[0]

            if id_var not in self.sym_table:
                self._error(f"variable '{id_var}' no declarada")

            return

        # Escritura:
        # escribe numero;
        if etiqueta == "escribe":
            self.tipoSubTree(hijos[0])
            return

        # Condicional sin sino
        if etiqueta == "si":
            condicion = hijos[0]
            instrucciones = hijos[1:]

            self._verify_condition(condicion, "si")
            self._verify_block(instrucciones)

            return

        # Condicional con sino
        if etiqueta == "si_sino":
            condicion, bloque_si, bloque_sino = hijos

            self._verify_condition(condicion, "si")
            self._verify_block(bloque_si)
            self._verify_block(bloque_sino)

            return

        # Ciclo mientras
        if etiqueta == "mientras":
            condicion, instrucciones = hijos

            self._verify_condition(condicion, "mientras")
            self._verify_block(instrucciones)

            return

        # Ciclo para
        if etiqueta == "para":
            id_var, inicio, fin, instrucciones = hijos

            if id_var not in self.sym_table:
                self._error(
                    f"variable de control '{id_var}' no declarada"
                )

            elif self.sym_table[id_var] != "entero":
                self._error(
                    f"la variable de control '{id_var}' debe ser "
                    f"de tipo 'entero', pero es "
                    f"'{self.sym_table[id_var]}'"
                )

            tipo_inicio = self.tipoSubTree(inicio)
            tipo_fin = self.tipoSubTree(fin)

            if (
                tipo_inicio is not None
                and tipo_inicio != "entero"
            ):
                self._error(
                    "el valor inicial de 'para' debe ser "
                    f"'entero', pero se obtuvo '{tipo_inicio}'"
                )

            if (
                tipo_fin is not None
                and tipo_fin != "entero"
            ):
                self._error(
                    "el valor final de 'para' debe ser "
                    f"'entero', pero se obtuvo '{tipo_fin}'"
                )

            self._verify_block(instrucciones)

            return

        # Permite comprobar directamente una expresión.
        self.tipoSubTree(ast)

    def tipoSubTree(self, ast):
        """Obtiene el tipo de una expresión y reporta sus errores."""

        # En Python, bool también es una subclase de int.
        # Por eso debemos comprobar bool antes que int.
        if isinstance(ast, bool):
            return "booleano"

        if isinstance(ast, int):
            return "entero"

        if isinstance(ast, float):
            return "real"

        # Literales o identificadores representados como texto.
        if isinstance(ast, str):

            if ast.startswith('"') and ast.endswith('"'):
                return "cadena"

            if ast in self.LITERALES_BOOLEANOS:
                return "booleano"

            if re.fullmatch(r"-?\d+", ast):
                return "entero"

            if re.fullmatch(r"-?\d*\.\d+", ast):
                return "real"

            if ast in self.sym_table:
                return self.sym_table[ast]

            self._error(f"variable '{ast}' no declarada")
            return None

        if ast is None or not hasattr(ast, "etiqueta"):
            return None

        etiqueta = ast.etiqueta()
        hijos = ast.hijos() or []

        # Operadores aritméticos
        if (
            etiqueta in ("+", "-", "*", "/")
            and len(hijos) == 2
        ):
            tipo_izquierdo = self.tipoSubTree(hijos[0])
            tipo_derecho = self.tipoSubTree(hijos[1])

            if (
                tipo_izquierdo is None
                or tipo_derecho is None
            ):
                return None

            if (
                tipo_izquierdo not in self.TIPOS_NUMERICOS
                or tipo_derecho not in self.TIPOS_NUMERICOS
            ):
                self._error(
                    f"el operador '{etiqueta}' requiere valores "
                    f"numéricos, pero recibió '{tipo_izquierdo}' "
                    f"y '{tipo_derecho}'"
                )

                return None

            # En Python, una división siempre produce un valor real.
            if (
                etiqueta == "/"
                or "real" in (tipo_izquierdo, tipo_derecho)
            ):
                return "real"

            return "entero"

        # Operadores de comparación
        if (
            etiqueta in ("==", "!=", "<", ">", "<=", ">=")
            and len(hijos) == 2
        ):
            tipo_izquierdo = self.tipoSubTree(hijos[0])
            tipo_derecho = self.tipoSubTree(hijos[1])

            if (
                tipo_izquierdo is None
                or tipo_derecho is None
            ):
                return None

            ambos_numericos = (
                tipo_izquierdo in self.TIPOS_NUMERICOS
                and tipo_derecho in self.TIPOS_NUMERICOS
            )

            if etiqueta in ("==", "!="):

                if (
                    tipo_izquierdo != tipo_derecho
                    and not ambos_numericos
                ):
                    self._error(
                        f"no se pueden comparar con '{etiqueta}' "
                        f"los tipos '{tipo_izquierdo}' y "
                        f"'{tipo_derecho}'"
                    )

                    return None

            elif not ambos_numericos:
                self._error(
                    f"el operador '{etiqueta}' requiere valores "
                    f"numéricos, pero recibió '{tipo_izquierdo}' "
                    f"y '{tipo_derecho}'"
                )

                return None

            return "booleano"

        # Operadores booleanos binarios
        if (
            etiqueta in ("y", "o")
            and len(hijos) == 2
        ):
            tipo_izquierdo = self.tipoSubTree(hijos[0])
            tipo_derecho = self.tipoSubTree(hijos[1])

            if (
                tipo_izquierdo is None
                or tipo_derecho is None
            ):
                return None

            if (
                tipo_izquierdo != "booleano"
                or tipo_derecho != "booleano"
            ):
                self._error(
                    f"el operador '{etiqueta}' requiere valores "
                    f"booleanos, pero recibió '{tipo_izquierdo}' "
                    f"y '{tipo_derecho}'"
                )

                return None

            return "booleano"

        # Operador booleano unario
        if etiqueta == "no" and len(hijos) == 1:
            tipo_operando = self.tipoSubTree(hijos[0])

            if tipo_operando is None:
                return None

            if tipo_operando != "booleano":
                self._error(
                    "el operador 'no' requiere un valor booleano, "
                    f"pero recibió '{tipo_operando}'"
                )

                return None

            return "booleano"

        return None
