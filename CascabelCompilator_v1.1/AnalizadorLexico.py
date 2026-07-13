from rply import LexerGenerator


class Lexer:
    """Construye el analizador léxico del lenguaje Cascabel."""

    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # Palabras reservadas
        self.lexer.add("PROGRAMA", r"\bprograma\b")
        self.lexer.add("SINO", r"\bsino\b")
        self.lexer.add("MIENTRAS", r"\bmientras\b")
        self.lexer.add("SI", r"\bsi\b")
        self.lexer.add("ENTONCES", r"\bentonces\b")
        self.lexer.add("PARA", r"\bpara\b")
        self.lexer.add("DESDE", r"\bdesde\b")
        self.lexer.add("HASTA", r"\bhasta\b")
        self.lexer.add("OP_LECTURA", r"\blee\b")
        self.lexer.add("OP_ESCRITURA", r"\bescribe\b")

        # Tipos de datos
        self.lexer.add("TIPO", r"\b(?:entero|real|booleano|cadena)\b")

        # Literales. Los números no incluyen el signo: el parser procesa
        # el signo menos como un operador unario y evita confundir a-5.
        self.lexer.add("LIT_CADENA", r'"(\\.|[^\\"])*"')
        self.lexer.add("LIT_REAL", r"\d+\.\d+")
        self.lexer.add("LIT_ENTERO", r"\d+")
        self.lexer.add(
            "LIT_BOOL",
            r"\b(?:Verdadero|Falso|verdadero|falso|True|False|true|false)\b",
        )

        # Operadores de comparación y asignación.
        # Las comparaciones deben registrarse antes que '='.
        self.lexer.add("OP_COMP", r"==|!=|<=|>=|>|<")
        self.lexer.add("OP_ASIGN", r"=")

        # Operadores aritméticos separados por precedencia.
        self.lexer.add("OP_SUMA", r"\+")
        self.lexer.add("OP_RESTA", r"-")
        self.lexer.add("OP_MULT", r"\*")
        self.lexer.add("OP_DIV", r"/")

        # Operadores booleanos separados para construir una gramática clara.
        self.lexer.add("OP_NOT", r"\bno\b")
        self.lexer.add("OP_Y", r"\by\b")
        self.lexer.add("OP_O", r"\bo\b")

        # Identificadores: siempre después de palabras reservadas y booleanos.
        self.lexer.add("ID", r"[a-zA-Z_][a-zA-Z0-9_]*")

        # Símbolos
        self.lexer.add("LLAV_ABRE", r"\{")
        self.lexer.add("LLAV_CIERRA", r"\}")
        self.lexer.add("PAR_IZQ", r"\(")
        self.lexer.add("PAR_DER", r"\)")
        self.lexer.add("PUNTOYCOMA", r";")

        # Espacios, saltos de línea y comentarios de una línea.
        self.lexer.ignore(r"\s+")
        self.lexer.ignore(r"\#[^\n]*")

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
