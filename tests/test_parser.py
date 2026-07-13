"""Pruebas del analizador sintáctico y del AST."""

from __future__ import annotations

import pytest

from helpers import parse_source


def test_respeta_precedencia_aritmetica():
    source = "programa { entero resultado = 2 + 3 * 4; }"

    ast, _symbols = parse_source(source)
    declaration = ast.hijos()[0]
    expression = declaration.hijos()[2]

    assert expression.etiqueta() == "+"
    assert expression.hijos()[0] == "2"
    assert expression.hijos()[1].etiqueta() == "*"
    assert expression.hijos()[1].hijos() == ["3", "4"]


def test_parentesis_cambian_la_precedencia():
    source = "programa { entero resultado = (2 + 3) * 4; }"

    ast, _symbols = parse_source(source)
    expression = ast.hijos()[0].hijos()[2]

    assert expression.etiqueta() == "*"
    assert expression.hijos()[0].etiqueta() == "+"


def test_y_tiene_mayor_precedencia_que_o():
    source = (
        "programa { "
        "booleano valor = Verdadero o Falso y Falso; "
        "}"
    )

    ast, _symbols = parse_source(source)
    expression = ast.hijos()[0].hijos()[2]

    assert expression.etiqueta() == "o"
    assert expression.hijos()[1].etiqueta() == "y"


def test_construye_condicional_con_sino():
    source = """
    programa {
      si Verdadero entonces {
        escribe "si";
      } sino {
        escribe "no";
      }
    }
    """

    ast, _symbols = parse_source(source)
    conditional = ast.hijos()[0]

    assert conditional.etiqueta() == "si_sino"
    assert len(conditional.hijos()) == 3
    assert conditional.hijos()[1][0].etiqueta() == "escribe"
    assert conditional.hijos()[2][0].etiqueta() == "escribe"


def test_final_inesperado_produce_error_sintactico():
    source = "programa { entero numero = 1;"

    with pytest.raises(ValueError, match="terminó inesperadamente"):
        parse_source(source)
