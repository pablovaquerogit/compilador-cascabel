"""Pruebas de generación y ejecución de código Python."""

from __future__ import annotations

import runpy

from helpers import generate_python


def test_genera_y_ejecuta_precedencia_correcta(tmp_path, capsys):
    source = """
    programa {
      entero resultado1 = 2 + 3 * 4;
      entero resultado2 = (2 + 3) * 4;
      escribe resultado1;
      escribe resultado2;
    }
    """
    output_path = tmp_path / "precedencia.py"

    generated = generate_python(source, output_path)
    runpy.run_path(str(output_path), run_name="__main__")
    output = capsys.readouterr().out.strip().splitlines()

    assert "resultado1 = (2 + (3 * 4))" in generated
    assert "resultado2 = ((2 + 3) * 4)" in generated
    assert output == ["14", "20"]


def test_genera_booleanos_y_negacion_numerica(tmp_path):
    source = """
    programa {
      entero numero = -5;
      booleano activo = no Falso;
      escribe numero;
      escribe activo;
    }
    """
    output_path = tmp_path / "booleanos.py"

    generated = generate_python(source, output_path)

    assert "numero = (-5)" in generated
    assert "activo = (not False)" in generated
    compile(generated, str(output_path), "exec")


def test_genera_pass_en_bloques_vacios(tmp_path):
    source = """
    programa {
      si Verdadero entonces {
      } sino {
      }

      mientras Falso {
      }

      entero i = 1;
      para i desde 1 hasta 0 {
      }
    }
    """
    output_path = tmp_path / "bloques_vacios.py"

    generated = generate_python(source, output_path)

    assert generated.count("pass") == 4
    compile(generated, str(output_path), "exec")


def test_interpolacion_de_variable_en_cadena(tmp_path, capsys):
    source = """
    programa {
      entero cantidad = 3;
      escribe "Cantidad: $cantidad";
    }
    """
    output_path = tmp_path / "interpolacion.py"

    generated = generate_python(source, output_path)
    runpy.run_path(str(output_path), run_name="__main__")
    output = capsys.readouterr().out.strip()

    assert "str(cantidad)" in generated
    assert output == "Cantidad: 3"
