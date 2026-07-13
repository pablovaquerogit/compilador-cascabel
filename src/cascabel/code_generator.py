"""Generación de código Python a partir del AST de Cascabel."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, TextIO


class CodeGenerator:
    """Traduce un árbol de sintaxis abstracta de Cascabel a Python."""

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

    DEFAULT_VALUES = {
        "entero": "0",
        "real": "0.0",
        "cadena": '""',
        "booleano": "False",
    }

    NUMERIC_PATTERN = re.compile(r"\d+(?:\.\d+)?")
    INTERPOLATION_PATTERN = re.compile(r"(\$[A-Za-z_][A-Za-z0-9_]*)")

    def __init__(
        self,
        symbols: Mapping[str, str],
        output_path: str | Path = "out.py",
    ) -> None:
        self.symbols = symbols
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output: TextIO = self.output_path.open(
            "w",
            encoding="utf-8",
            newline="\n",
        )
        self.indent = 0
        self._closed = False

    def __enter__(self) -> "CodeGenerator":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        """Cierra el archivo de salida de forma segura."""
        if not self._closed:
            self.output.close()
            self._closed = True

    def generate(self, ast: Any) -> None:
        """Genera un programa Python completo desde el AST recibido."""
        self._ensure_open()
        self.output.write(
            "# Código generado automáticamente por el compilador Cascabel.\n\n"
        )
        self._generate_node(ast)

    def _ensure_open(self) -> None:
        if self._closed:
            raise ValueError("el archivo de salida ya está cerrado")

    def _indentation(self) -> str:
        return "    " * self.indent

    def _write_line(self, text: str = "") -> None:
        self.output.write(f"{self._indentation()}{text}\n")

    def _generate_node(self, node: Any) -> None:
        if isinstance(node, list):
            for child in node:
                self._generate_node(child)
            return

        if node is None:
            return

        if not hasattr(node, "etiqueta"):
            raise TypeError(
                "se esperaba un nodo del AST, pero se recibió "
                f"{type(node).__name__}"
            )

        tag = node.etiqueta()
        children = node.hijos() or []

        if tag == "programa":
            self._generate_node(children)
            return

        if tag == "declara":
            data_type, variable = children
            try:
                default_value = self.DEFAULT_VALUES[data_type]
            except KeyError as error:
                raise ValueError(
                    f"tipo de dato no soportado: '{data_type}'"
                ) from error

            self._write_line(f"{variable} = {default_value}")
            return

        if tag == "declara_asigna":
            _data_type, variable, expression = children
            self.output.write(f"{self._indentation()}{variable} = ")
            self._generate_expression(expression)
            self.output.write("\n")
            return

        if tag == "=":
            variable, expression = children
            self.output.write(f"{self._indentation()}{variable} = ")
            self._generate_expression(expression)
            self.output.write("\n")
            return

        if tag == "lee":
            self._generate_read(children[0])
            return

        if tag == "escribe":
            self.output.write(f"{self._indentation()}print(")
            self._generate_expression(children[0])
            self.output.write(")\n")
            return

        if tag == "si":
            condition = children[0]
            body = children[1:]
            self.output.write(f"{self._indentation()}if ")
            self._generate_expression(condition)
            self.output.write(":\n")
            self._generate_block(body)
            return

        if tag == "si_sino":
            condition, then_block, else_block = children
            self.output.write(f"{self._indentation()}if ")
            self._generate_expression(condition)
            self.output.write(":\n")
            self._generate_block(then_block)
            self._write_line("else:")
            self._generate_block(else_block)
            return

        if tag == "mientras":
            condition, body = children
            self.output.write(f"{self._indentation()}while ")
            self._generate_expression(condition)
            self.output.write(":\n")
            self._generate_block(body)
            return

        if tag == "para":
            variable, start, end, body = children
            self.output.write(f"{self._indentation()}for {variable} in range(")
            self._generate_expression(start)
            self.output.write(", (")
            self._generate_expression(end)
            self.output.write(") + 1):\n")
            self._generate_block(body)
            return

        raise ValueError(f"instrucción del AST no soportada: '{tag}'")

    def _generate_block(self, block: Any) -> None:
        instructions = block if isinstance(block, list) else [block]
        instructions = [item for item in instructions if item is not None]

        self.indent += 1
        try:
            if not instructions:
                self._write_line("pass")
                return

            for instruction in instructions:
                self._generate_node(instruction)
        finally:
            self.indent -= 1

    def _generate_read(self, variable: str) -> None:
        data_type = self.symbols.get(variable)

        conversions = {
            "entero": "int(input())",
            "real": "float(input())",
            "cadena": "input()",
            "booleano": (
                "input().strip().lower() in "
                "('verdadero', 'true', '1', 'si', 'sí')"
            ),
        }

        if data_type not in conversions:
            raise ValueError(
                f"no se puede generar la lectura de '{variable}': "
                "tipo desconocido"
            )

        self._write_line(f"{variable} = {conversions[data_type]}")

    def _generate_expression(self, expression: Any) -> None:
        if isinstance(expression, bool):
            self.output.write("True" if expression else "False")
            return

        if isinstance(expression, (int, float)):
            self.output.write(str(expression))
            return

        if isinstance(expression, str):
            self._generate_text_expression(expression)
            return

        if expression is None or not hasattr(expression, "etiqueta"):
            raise TypeError(
                "expresión no válida para generar código: "
                f"{type(expression).__name__}"
            )

        tag = expression.etiqueta()
        children = expression.hijos() or []

        if tag == "no":
            self.output.write("(not ")
            self._generate_expression(children[0])
            self.output.write(")")
            return

        if tag == "negativo":
            self.output.write("(-")
            self._generate_expression(children[0])
            self.output.write(")")
            return

        if tag in {"+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">="}:
            left, right = children
            self.output.write("(")
            self._generate_expression(left)
            self.output.write(f" {tag} ")
            self._generate_expression(right)
            self.output.write(")")
            return

        if tag in {"y", "o"}:
            left, right = children
            operator = "and" if tag == "y" else "or"
            self.output.write("(")
            self._generate_expression(left)
            self.output.write(f" {operator} ")
            self._generate_expression(right)
            self.output.write(")")
            return

        raise ValueError(f"expresión del AST no soportada: '{tag}'")

    def _generate_text_expression(self, value: str) -> None:
        if value in self.BOOLEAN_LITERALS:
            self.output.write(self.BOOLEAN_LITERALS[value])
            return

        if self.NUMERIC_PATTERN.fullmatch(value):
            self.output.write(value)
            return

        if value.startswith('"') and value.endswith('"'):
            if "$" in value:
                self.output.write(self._string_to_code(value))
            else:
                self.output.write(value)
            return

        self.output.write(value)

    def _string_to_code(self, value: str) -> str:
        """Convierte una cadena con ``$variable`` en concatenación Python."""
        content = value[1:-1]
        parts = self.INTERPOLATION_PATTERN.split(content)
        generated_parts: list[str] = []

        for part in parts:
            if not part:
                continue

            if part.startswith("$"):
                generated_parts.append(f"str({part[1:]})")
            else:
                generated_parts.append(repr(part))

        return " + ".join(generated_parts) if generated_parts else "''"
