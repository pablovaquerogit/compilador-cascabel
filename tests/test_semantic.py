"""Pruebas del analizador semántico."""

from __future__ import annotations

from helpers import semantic_errors


def test_programa_valido_no_tiene_errores():
    source = """
    programa {
      entero numero = 3;
      real promedio = 2.5;
      booleano activo = Verdadero;
      cadena mensaje = "Hola";
      numero = numero + 1;
      escribe mensaje;
    }
    """

    assert semantic_errors(source) == 0


def test_detecta_errores_dentro_de_mientras():
    source = """
    programa {
      entero contador = 1;
      mientras contador {
        desconocida = 34.5;
      }
    }
    """

    assert semantic_errors(source) == 2


def test_detecta_declaracion_duplicada():
    source = """
    programa {
      entero edad;
      cadena edad;
    }
    """

    assert semantic_errors(source) == 1


def test_detecta_operacion_aritmetica_con_booleano():
    source = """
    programa {
      booleano activo = Verdadero;
      entero total = 4;
      total = activo + total;
    }
    """

    assert semantic_errors(source) == 1


def test_variable_de_control_para_debe_ser_entera():
    source = """
    programa {
      real indice = 1.0;
      para indice desde 1 hasta 3 {
        escribe indice;
      }
    }
    """

    assert semantic_errors(source) == 1
