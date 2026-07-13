"""Punto de entrada del compilador para el lenguaje Cascabel."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

from rply.errors import LexingError

from .lexer import Lexer
from .semantic import SemAnalyzer
from .parser import Parser
from .code_generator import CodeGenerator


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parents[1]
EXAMPLES_DIR = PROJECT_ROOT / "examples"
GENERATED_DIR = PROJECT_ROOT / "generated"
AST_PATH = GENERATED_DIR / "AST.txt"
OUTPUT_PATH = GENERATED_DIR / "out.py"


class Colors:
    """Códigos ANSI usados para hacer más legible la salida en Terminal."""

    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_header() -> None:
    print(Colors.GREEN)
    print("\n\t\t-----------------------------------------------------------")
    print("\t\t* Compilador para el lenguaje Cascabel versión 1.1       *")
    print("\t\t*                                                         *")
    print("\t\t*          Facultad de Ingeniería - UNAM                  *")
    print("\t\t*          Lenguajes Formales y Autómatas                 *")
    print("\t\t-----------------------------------------------------------\n")
    print(Colors.RESET, end="")


def print_section(title: str) -> None:
    print(f"{Colors.GREEN}\n----------------------------------------------------")
    print(title)
    print(f"----------------------------------------------------\n{Colors.RESET}")


def request_source_file() -> Path | None:
    print("Ingrese el nombre del programa fuente o 'salir' para terminar:")
    value = input("\n [default: holamundo.casc] > ").strip()

    if value.lower() == "salir":
        return None

    if not value:
        value = "holamundo.casc"

    requested_path = Path(value).expanduser()

    if requested_path.is_absolute():
        source_path = requested_path
    elif requested_path.exists():
        source_path = requested_path.resolve()
    else:
        direct_path = EXAMPLES_DIR / requested_path

        if direct_path.is_file():
            source_path = direct_path
        else:
            matches = list(EXAMPLES_DIR.rglob(requested_path.name))

            if len(matches) == 1:
                source_path = matches[0]
            elif len(matches) > 1:
                locations = ", ".join(
                    str(path.relative_to(PROJECT_ROOT)) for path in matches
                )
                raise ValueError(
                    f"hay varios ejemplos llamados '{requested_path.name}': "
                    f"{locations}"
                )
            else:
                source_path = direct_path

    if not source_path.is_file():
        raise FileNotFoundError(
            f"el programa fuente '{source_path}' no existe"
        )

    return source_path.resolve()


def request_stage() -> int:
    while True:
        print(
            "\n* Ingrese el número de etapa hasta la cual desea "
            "ejecutar el proceso de compilación:\n"
        )
        print("(1) Análisis léxico")
        print("(2) Análisis sintáctico")
        print("(3) Análisis semántico")
        print("(4) Generación de código")
        print("(5) Ejecución del programa objeto")

        value = input("\n [default: 1] > ").strip()

        if not value:
            return 1

        try:
            stage = int(value)
        except ValueError:
            print(f"\n{Colors.RED}Ingrese un número del 1 al 5.{Colors.RESET}")
            continue

        if 1 <= stage <= 5:
            return stage

        print(f"\n{Colors.RED}Ingrese un número del 1 al 5.{Colors.RESET}")


def read_source(source_path: Path) -> str:
    try:
        return source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(
            "el archivo fuente no está codificado en UTF-8"
        ) from error


def show_source(source_code: str) -> None:
    print(f"\nPROGRAMA FUENTE:\n{Colors.CYAN}")

    for line_number, line in enumerate(source_code.splitlines(), start=1):
        print(f"{line_number:>3} {line}")

    print(Colors.RESET)


def lexical_analysis(source_code: str):
    print_section("Iniciando análisis léxico")
    show_source(source_code)

    lexer = Lexer().get_lexer()
    print(f"\nTOKENS IDENTIFICADOS:\n{Colors.YELLOW}")

    try:
        tokens = list(lexer.lex(source_code))
    except LexingError as error:
        position = error.getsourcepos()
        line = position.lineno if position is not None else "desconocida"
        column = position.colno if position is not None else "desconocida"
        print(Colors.RESET)
        print(
            f"{Colors.RED}ERROR LÉXICO: token no identificado "
            f"en la línea {line}, columna {column}.{Colors.RESET}"
        )
        return None

    for token in tokens:
        print(token)

    print(Colors.RESET)
    print("\n* PROGRAMA LÉXICAMENTE CORRECTO")
    return lexer


def syntactic_analysis(lexer, source_code: str):
    print_section("Iniciando análisis sintáctico")

    parser_builder = Parser()
    parser_builder.parse()
    parser = parser_builder.get_parser()

    try:
        ast = parser.parse(lexer.lex(source_code))
    except ValueError:
        # El manejador del parser ya mostró el error sintáctico específico.
        return None, None
    except Exception as error:
        print(
            f"\n{Colors.RED}ERROR INTERNO DEL ANALIZADOR SINTÁCTICO: "
            f"{type(error).__name__}: {error}{Colors.RESET}"
        )
        return None, None

    with AST_PATH.open("w", encoding="utf-8") as ast_file:
        ast.print(ast_file)

    print(f"\nÁRBOL DE SINTAXIS ABSTRACTA:\n{Colors.YELLOW}")
    print(AST_PATH.read_text(encoding="utf-8"))

    symbol_table = parser_builder.get_symbols()
    if symbol_table:
        print(f"{Colors.RESET}\nTabla de símbolos:\n")
        print(dict(symbol_table))

    print(Colors.RESET)
    print("\n* PROGRAMA SINTÁCTICAMENTE CORRECTO")
    return ast, symbol_table


def semantic_analysis(ast, symbol_table) -> bool:
    print_section("Iniciando análisis semántico")

    analyzer = SemAnalyzer(symbol_table)
    error_count = analyzer.verify(ast)

    if error_count > 0:
        print(f"\nERRORES SEMÁNTICOS: {error_count}")
        return False

    print("\n* PROGRAMA SEMÁNTICAMENTE CORRECTO")
    return True


def generate_code(ast, symbol_table) -> bool:
    print_section("Generación de código")

    try:
        with CodeGenerator(symbol_table, OUTPUT_PATH) as generator:
            generator.generate(ast)
    except Exception as error:
        print(
            f"\n{Colors.RED}ERROR DEL GENERADOR DE CÓDIGO: "
            f"{type(error).__name__}: {error}{Colors.RESET}"
        )
        return False

    print(f"\n* PROGRAMA OBJETO (CÓDIGO GENERADO):\n{Colors.YELLOW}{Colors.BOLD}")
    print(OUTPUT_PATH.read_text(encoding="utf-8"))
    print(Colors.RESET)
    return True


def execute_generated_program() -> bool:
    print_section("Ejecución del programa objeto")
    print(f"{Colors.BLUE}{Colors.BOLD}")

    try:
        runpy.run_path(str(OUTPUT_PATH), run_name="__main__")
    except Exception as error:
        print(
            f"\n{Colors.RED}ERROR DURANTE LA EJECUCIÓN DEL PROGRAMA "
            f"OBJETO: {type(error).__name__}: {error}{Colors.RESET}"
        )
        return False
    finally:
        print(Colors.RESET)

    return True


def main() -> int:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    print_header()

    try:
        source_path = request_source_file()
        if source_path is None:
            return 0

        stage = request_stage()
        source_code = read_source(source_path)

        lexer = lexical_analysis(source_code)
        if lexer is None or stage == 1:
            return 1 if lexer is None else 0

        ast, symbol_table = syntactic_analysis(lexer, source_code)
        if ast is None or stage == 2:
            return 1 if ast is None else 0

        semantic_ok = semantic_analysis(ast, symbol_table)
        if not semantic_ok or stage == 3:
            return 1 if not semantic_ok else 0

        generated_ok = generate_code(ast, symbol_table)
        if not generated_ok or stage == 4:
            return 1 if not generated_ok else 0

        return 0 if execute_generated_program() else 1

    except (EOFError, KeyboardInterrupt):
        print(f"\n{Colors.YELLOW}Proceso cancelado por el usuario.{Colors.RESET}")
        return 130
    except (OSError, ValueError) as error:
        print(f"\n{Colors.RED}ERROR: {error}{Colors.RESET}")
        return 1
    finally:
        print(f"{Colors.GREEN}\nCompilador finalizado.\n{Colors.RESET}")


if __name__ == "__main__":
    sys.exit(main())
