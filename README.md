# Compilador Cascabel

[![Pruebas automáticas](https://github.com/pablovaquerogit/compilador-cascabel/actions/workflows/tests.yml/badge.svg)](https://github.com/pablovaquerogit/compilador-cascabel/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)

Compilador educativo para el lenguaje **Cascabel**, desarrollado en Python. El proyecto implementa las etapas principales de un compilador: análisis léxico, análisis sintáctico, análisis semántico, construcción de un árbol de sintaxis abstracta y generación de código Python ejecutable.

## Descripción

Cascabel es un lenguaje educativo con sintaxis en español. Este compilador recibe un archivo con extensión `.casc`, valida su estructura y sus tipos de datos, construye un AST y traduce el programa a Python.

El proyecto fue desarrollado de forma individual como parte de la asignatura **Lenguajes Formales y Autómatas** de la Facultad de Ingeniería de la UNAM. La idea académica del lenguaje fue proporcionada por el profesor; la implementación completa del compilador fue realizada por **Pablo Vaquero**.

## Características

- Reconocimiento de palabras reservadas, identificadores, literales y operadores.
- Precedencia correcta para operadores aritméticos y booleanos.
- Construcción y visualización del árbol de sintaxis abstracta.
- Tabla de símbolos y detección de declaraciones duplicadas.
- Validación de tipos, variables no declaradas y condiciones booleanas.
- Soporte para declaraciones, asignaciones, lectura y escritura.
- Estructuras `si`, `sino`, `mientras` y `para`.
- Generación de código Python.
- Interpolación de variables dentro de cadenas mediante `$variable`.
- Detección de errores léxicos, sintácticos y semánticos.
- Pruebas automáticas con `pytest`.
- Integración continua con GitHub Actions.

## Etapas de compilación

El programa permite detenerse en cualquiera de las siguientes etapas:

1. **Análisis léxico:** identifica y clasifica los tokens.
2. **Análisis sintáctico:** valida la gramática y construye el AST.
3. **Análisis semántico:** comprueba declaraciones, tipos y condiciones.
4. **Generación de código:** traduce el AST a Python.
5. **Ejecución:** ejecuta el programa Python generado.

## Sintaxis básica

### Tipos de datos

| Tipo Cascabel | Equivalente en Python |
|---|---|
| `entero` | `int` |
| `real` | `float` |
| `booleano` | `bool` |
| `cadena` | `str` |

### Ejemplo

```cascabel
programa {
  entero cantidad = 6;
  entero resultado = 2 + 3 * 4;

  escribe "Cantidad: $cantidad";
  escribe resultado;

  si cantidad > 0 entonces {
    escribe "La cantidad es positiva";
  } sino {
    escribe "La cantidad no es positiva";
  }
}
```

Código Python generado:

```python
cantidad = 6
resultado = (2 + (3 * 4))

print("Cantidad: " + str(cantidad))
print(resultado)

if (cantidad > 0):
    print("La cantidad es positiva")
else:
    print("La cantidad no es positiva")
```

## Estructura del proyecto

```text
compilador-cascabel/
├── .github/
│   └── workflows/
│       └── tests.yml
├── docs/
│   └── README-original.txt
├── examples/
│   ├── valid/
│   ├── lexical/
│   └── invalid/
│       ├── lexical/
│       ├── syntax/
│       ├── semantic/
│       └── mixed/
├── generated/
├── src/
│   └── cascabel/
│       ├── __init__.py
│       ├── __main__.py
│       ├── ast.py
│       ├── cli.py
│       ├── code_generator.py
│       ├── lexer.py
│       ├── parser.py
│       └── semantic.py
├── tests/
├── LICENSE
├── README.md
├── pyproject.toml
├── pytest.ini
├── requirements.txt
└── requirements-dev.txt
```

## Requisitos

- Python 3.10 o superior
- `rply`
- `nltk`

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/pablovaquerogit/compilador-cascabel.git
cd compilador-cascabel
```

Se recomienda crear un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows:

```powershell
.venv\Scripts\activate
```

Instala el proyecto:

```bash
python3 -m pip install -e .
```

Para instalar también las herramientas de desarrollo:

```bash
python3 -m pip install -r requirements-dev.txt
```

## Uso

Ejecuta el compilador con:

```bash
cascabel
```

También puedes usar:

```bash
python3 -m cascabel
```

El programa solicitará:

1. El nombre o la ruta del archivo `.casc`.
2. La etapa hasta la cual deseas ejecutar el proceso.

Al presionar Enter sin escribir un archivo, se utiliza `holamundo.casc` como ejemplo predeterminado.

Los archivos generados se guardan en la carpeta `generated/`.

## Ejemplos disponibles

Los programas están organizados en:

- `examples/valid/`: programas válidos.
- `examples/lexical/`: ejemplos para observar tokens.
- `examples/invalid/lexical/`: errores léxicos.
- `examples/invalid/syntax/`: errores sintácticos.
- `examples/invalid/semantic/`: errores semánticos.
- `examples/invalid/mixed/`: programas con errores de varias categorías.

Entre los ejemplos válidos se incluyen un programa Hola Mundo, el cálculo de la serie de Fibonacci, pruebas de precedencia y estructuras con bloques vacíos.

## Pruebas automáticas

Ejecuta toda la suite con:

```bash
python3 -m pytest -q
```

La suite contiene **18 pruebas** que cubren:

- análisis léxico;
- precedencia y construcción del AST;
- validaciones semánticas;
- generación y ejecución de Python.

GitHub Actions ejecuta estas pruebas automáticamente en cada `push` y en los pull requests dirigidos a `main`.

## Alcance actual

El compilador está orientado a fines educativos. Actualmente trabaja con una tabla de símbolos global y no incorpora funciones, arreglos, módulos ni optimizaciones de código.

## Autor

**Pablo Vaquero**

- GitHub: [@pablovaquerogit](https://github.com/pablovaquerogit)

## Contexto académico

La propuesta del lenguaje Cascabel fue proporcionada como parte de una actividad académica. El diseño e implementación del lexer, parser, análisis semántico, AST, generador de código, pruebas y organización del repositorio fueron realizados individualmente por el autor.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para conocer los términos.
