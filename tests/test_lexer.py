"""Pruebas del analizador léxico."""

from __future__ import annotations

import pytest
from rply.errors import LexingError

from helpers import tokenize


def test_reconoce_palabras_reservadas_y_operadores_booleanos():
    source = """
    programa {
      booleano activo = verdadero;
      booleano resultado = no activo o falso y Verdadero;
    }
    """

    tokens = tokenize(source)
    token_types = [token.gettokentype() for token in tokens]

    assert "PROGRAMA" in token_types
    assert token_types.count("TIPO") == 2
    assert token_types.count("LIT_BOOL") == 3
    assert "OP_NOT" in token_types
    assert "OP_O" in token_types
    assert "OP_Y" in token_types


def test_palabra_reservada_no_divide_un_identificador():
    source = "programa { entero sistema = 1; entero programador = 2; }"

    values_by_type = [
        (token.gettokentype(), token.value)
        for token in tokenize(source)
    ]

    assert ("ID", "sistema") in values_by_type
    assert ("ID", "programador") in values_by_type


def test_resta_y_numero_negativo_generan_tokens_separados():
    source = "programa { entero a = -5; entero b = a-3; }"

    tokens = tokenize(source)
    pairs = [(token.gettokentype(), token.value) for token in tokens]

    assert pairs.count(("OP_RESTA", "-")) == 2
    assert ("LIT_ENTERO", "5") in pairs
    assert ("LIT_ENTERO", "3") in pairs


def test_caracter_desconocido_produce_error_lexico():
    lexer_source = "programa { entero numero = 1 @ 2; }"

    with pytest.raises(LexingError):
        tokenize(lexer_source)
