"""Estructuras utilizadas para representar el AST de Cascabel."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, TextIO

from nltk.tree import Tree


class Arbol:
    """Representa un nodo del árbol de sintaxis abstracta.

    Cada nodo tiene una etiqueta y una lista de hijos. Los hijos pueden ser
    otros nodos, valores literales o listas de instrucciones usadas por los
    bloques del lenguaje Cascabel.
    """

    def __init__(self, etiqueta_raiz: str, hijos: list[Any] | None = None) -> None:
        if not isinstance(etiqueta_raiz, str) or not etiqueta_raiz.strip():
            raise ValueError("la etiqueta de un nodo debe ser un texto no vacío")

        if hijos is not None and not isinstance(hijos, list):
            raise TypeError("los hijos de un nodo deben proporcionarse como lista")

        self.label = etiqueta_raiz
        self.children = list(hijos) if hijos is not None else []

    def etiqueta(self) -> str:
        """Devuelve la etiqueta del nodo."""
        return self.label

    def hijos(self) -> list[Any]:
        """Devuelve los hijos directos del nodo."""
        return self.children

    def es_hoja(self) -> bool:
        """Indica si el nodo no contiene hijos."""
        return not self.children

    def recorrer(self) -> Iterator["Arbol"]:
        """Recorre en preorden todos los nodos del AST."""
        yield self

        for child in self.children:
            yield from _recorrer_nodos(child)

    def to_nltk_tree(self) -> Tree:
        """Convierte el AST a un árbol de NLTK para visualizarlo."""
        converted = _to_nltk_tree(self)

        if not isinstance(converted, Tree):
            raise TypeError("la raíz del AST debe convertirse en un árbol de NLTK")

        return converted

    def pretty_print(self, stream: TextIO | None = None) -> None:
        """Imprime el AST como diagrama ASCII en pantalla o en un archivo."""
        self.to_nltk_tree().pretty_print(
            stream=stream,
            unicodelines=False,
        )

    def print(self, stream: TextIO | None = None) -> None:
        """Mantiene compatibilidad con el nombre usado por ``main.py``."""
        self.pretty_print(stream)

    def __repr__(self) -> str:
        return f"Arbol(etiqueta={self.label!r}, hijos={self.children!r})"


def _recorrer_nodos(value: Any) -> Iterator[Arbol]:
    if isinstance(value, Arbol):
        yield from value.recorrer()
        return

    if isinstance(value, list):
        for item in value:
            yield from _recorrer_nodos(item)


def _to_nltk_tree(value: Any) -> Tree | str:
    """Convierte recursivamente nodos y valores a objetos compatibles con NLTK."""
    if isinstance(value, Arbol):
        converted_children: list[Tree | str] = []

        for child in value.hijos():
            if isinstance(child, list):
                converted_children.extend(_to_nltk_tree(item) for item in child)
            else:
                converted_children.append(_to_nltk_tree(child))

        return Tree(value.etiqueta(), converted_children)

    if value is None:
        return "None"

    return str(value)
