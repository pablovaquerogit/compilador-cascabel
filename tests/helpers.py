"""Funciones auxiliares usadas por las pruebas."""

from __future__ import annotations

from pathlib import Path

from cascabel.lexer import Lexer
from cascabel.semantic import SemAnalyzer
from cascabel.parser import Parser
from cascabel.code_generator import CodeGenerator


def tokenize(source: str):
    """Devuelve todos los tokens generados para un código Cascabel."""
    lexer = Lexer().get_lexer()
    return list(lexer.lex(source))


def parse_source(source: str):
    """Analiza un programa y devuelve su AST y tabla de símbolos."""
    lexer = Lexer().get_lexer()
    parser_builder = Parser()
    parser_builder.parse()
    parser = parser_builder.get_parser()
    ast = parser.parse(lexer.lex(source))
    return ast, parser_builder.get_symbols()


def semantic_errors(source: str) -> int:
    """Devuelve la cantidad de errores semánticos de un programa."""
    ast, symbols = parse_source(source)
    return SemAnalyzer(symbols).verify(ast)


def generate_python(source: str, output_path: Path) -> str:
    """Genera Python desde Cascabel y devuelve el texto producido."""
    ast, symbols = parse_source(source)
    errors = SemAnalyzer(symbols).verify(ast)
    if errors:
        raise AssertionError(
            f"el programa de prueba contiene {errors} error(es) semántico(s)"
        )

    with CodeGenerator(symbols, output_path) as generator:
        generator.generate(ast)

    return output_path.read_text(encoding="utf-8")
