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
        self._verify_duplicate_declarations()

        if ast is None or ast.etiqueta() != "programa":
            self._error("raíz inválida; se esperaba 'programa'")
            return self.num_errors

        self._verify_block(ast.hijos())
        return self.num_errors

    def _verify_duplicate_declarations(self):
        duplicates = getattr(
            self.sym_table,
            "duplicate_declarations",
            [],
        )

        for duplicate in duplicates:
            name = duplicate["name"]
            original_type = duplicate["original_type"]
            repeated_type = duplicate["repeated_type"]
            self._error(
                f"la variable '{name}' ya fue declarada como "
                f"'{original_type}' y no puede volver a declararse "
                f"como '{repeated_type}'"
            )

    def _error(self, message):
        print(f"**ERROR SEMÁNTICO: {message}**")
        self.num_errors += 1

    def _verify_block(self, instructions):
        if instructions is None:
            return

        if isinstance(instructions, list):
            for instruction in instructions:
                self.verifySubTree(instruction)
            return

        self.verifySubTree(instructions)

    def _verify_condition(self, condition, structure):
        condition_type = self.tipoSubTree(condition)

        if condition_type is None:
            return

        if condition_type != "booleano":
            self._error(
                f"la condición de '{structure}' debe ser booleana, "
                f"pero se obtuvo '{condition_type}'"
            )

    def verifySubTree(self, ast):
        if ast is None:
            return

        if isinstance(ast, list):
            self._verify_block(ast)
            return

        if not hasattr(ast, "etiqueta"):
            return

        tag = ast.etiqueta()
        children = ast.hijos() or []

        if tag == "declara":
            return

        if tag == "declara_asigna":
            declared_type, variable_name, expression = children
            expression_type = self.tipoSubTree(expression)

            if (
                expression_type is not None
                and declared_type != expression_type
            ):
                self._error(
                    f"se esperaba un valor '{declared_type}' "
                    f"para la variable '{variable_name}', pero se obtuvo "
                    f"'{expression_type}'"
                )
            return

        if tag == "=":
            variable_name, expression = children
            expression_type = self.tipoSubTree(expression)

            if variable_name not in self.sym_table:
                self._error(f"variable '{variable_name}' no declarada")
                return

            declared_type = self.sym_table[variable_name]

            if (
                expression_type is not None
                and declared_type != expression_type
            ):
                self._error(
                    f"se esperaba un valor '{declared_type}' "
                    f"para la variable '{variable_name}', pero se obtuvo "
                    f"'{expression_type}'"
                )
            return

        if tag == "lee":
            variable_name = children[0]

            if variable_name not in self.sym_table:
                self._error(f"variable '{variable_name}' no declarada")
            return

        if tag == "escribe":
            self.tipoSubTree(children[0])
            return

        if tag == "si":
            condition = children[0]
            instructions = children[1:]
            self._verify_condition(condition, "si")
            self._verify_block(instructions)
            return

        if tag == "si_sino":
            condition, if_block, else_block = children
            self._verify_condition(condition, "si")
            self._verify_block(if_block)
            self._verify_block(else_block)
            return

        if tag == "mientras":
            condition, instructions = children
            self._verify_condition(condition, "mientras")
            self._verify_block(instructions)
            return

        if tag == "para":
            variable_name, start, end, instructions = children

            if variable_name not in self.sym_table:
                self._error(
                    f"variable de control '{variable_name}' no declarada"
                )
            elif self.sym_table[variable_name] != "entero":
                self._error(
                    f"la variable de control '{variable_name}' debe ser "
                    f"de tipo 'entero', pero es "
                    f"'{self.sym_table[variable_name]}'"
                )

            start_type = self.tipoSubTree(start)
            end_type = self.tipoSubTree(end)

            if start_type is not None and start_type != "entero":
                self._error(
                    "el valor inicial de 'para' debe ser "
                    f"'entero', pero se obtuvo '{start_type}'"
                )

            if end_type is not None and end_type != "entero":
                self._error(
                    "el valor final de 'para' debe ser "
                    f"'entero', pero se obtuvo '{end_type}'"
                )

            self._verify_block(instructions)
            return

        self.tipoSubTree(ast)

    def tipoSubTree(self, ast):
        if isinstance(ast, bool):
            return "booleano"

        if isinstance(ast, int):
            return "entero"

        if isinstance(ast, float):
            return "real"

        if isinstance(ast, str):
            if ast.startswith('"') and ast.endswith('"'):
                return "cadena"

            if ast in self.LITERALES_BOOLEANOS:
                return "booleano"

            if re.fullmatch(r"\d+", ast):
                return "entero"

            if re.fullmatch(r"\d+\.\d+", ast):
                return "real"

            if ast in self.sym_table:
                return self.sym_table[ast]

            self._error(f"variable '{ast}' no declarada")
            return None

        if ast is None or not hasattr(ast, "etiqueta"):
            return None

        tag = ast.etiqueta()
        children = ast.hijos() or []

        if tag == "negativo" and len(children) == 1:
            operand_type = self.tipoSubTree(children[0])

            if operand_type is None:
                return None

            if operand_type not in self.TIPOS_NUMERICOS:
                self._error(
                    "el signo negativo requiere un valor numérico, "
                    f"pero recibió '{operand_type}'"
                )
                return None

            return operand_type

        if tag in ("+", "-", "*", "/") and len(children) == 2:
            left_type = self.tipoSubTree(children[0])
            right_type = self.tipoSubTree(children[1])

            if left_type is None or right_type is None:
                return None

            if (
                left_type not in self.TIPOS_NUMERICOS
                or right_type not in self.TIPOS_NUMERICOS
            ):
                self._error(
                    f"el operador '{tag}' requiere valores numéricos, "
                    f"pero recibió '{left_type}' y '{right_type}'"
                )
                return None

            if tag == "/" or "real" in (left_type, right_type):
                return "real"

            return "entero"

        if (
            tag in ("==", "!=", "<", ">", "<=", ">=")
            and len(children) == 2
        ):
            left_type = self.tipoSubTree(children[0])
            right_type = self.tipoSubTree(children[1])

            if left_type is None or right_type is None:
                return None

            both_numeric = (
                left_type in self.TIPOS_NUMERICOS
                and right_type in self.TIPOS_NUMERICOS
            )

            if tag in ("==", "!="):
                if left_type != right_type and not both_numeric:
                    self._error(
                        f"no se pueden comparar con '{tag}' los tipos "
                        f"'{left_type}' y '{right_type}'"
                    )
                    return None
            elif not both_numeric:
                self._error(
                    f"el operador '{tag}' requiere valores numéricos, "
                    f"pero recibió '{left_type}' y '{right_type}'"
                )
                return None

            return "booleano"

        if tag in ("y", "o") and len(children) == 2:
            left_type = self.tipoSubTree(children[0])
            right_type = self.tipoSubTree(children[1])

            if left_type is None or right_type is None:
                return None

            if left_type != "booleano" or right_type != "booleano":
                self._error(
                    f"el operador '{tag}' requiere valores booleanos, "
                    f"pero recibió '{left_type}' y '{right_type}'"
                )
                return None

            return "booleano"

        if tag == "no" and len(children) == 1:
            operand_type = self.tipoSubTree(children[0])

            if operand_type is None:
                return None

            if operand_type != "booleano":
                self._error(
                    "el operador 'no' requiere un valor booleano, "
                    f"pero recibió '{operand_type}'"
                )
                return None

            return "booleano"

        return None
