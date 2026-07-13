from rply import LexerGenerator


class Lexer:

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
        self.lexer.add(
            "TIPO",
            r"\b(?:entero|real|booleano|cadena)\b"
        )

        # Literales
        self.lexer.add(
            "LIT_CADENA",
            r'"(\\.|[^\\"])*"'
        )

        self.lexer.add(
            "LIT_REAL",
            r"-?\d*\.\d+"
        )

        self.lexer.add(
            "LIT_ENTERO",
            r"-?\d+"
        )

        self.lexer.add(
            "LIT_BOOL",
            r"\b(?:Verdadero|Falso|verdadero|falso|True|False|true|false)\b"
        )

        # Operadores
        self.lexer.add("OP_ARIT", r"\+|\-|\*|\/")
        self.lexer.add("OP_COMP", r"==|!=|<=|>=|>|<")
        self.lexer.add("OP_ASIGN", r"=")

        # El operador "no" es unario y necesita su propio token.
        self.lexer.add("OP_NOT", r"\bno\b")

        # Los operadores "y" y "o" son binarios.
        self.lexer.add("OP_BOOL", r"\b(?:y|o)\b")

        # Identificadores
        self.lexer.add(
            "ID",
            r"[a-zA-Z_][a-zA-Z0-9_]*"
        )

        # Símbolos
        self.lexer.add("LLAV_ABRE", r"\{")
        self.lexer.add("LLAV_CIERRA", r"\}")
        self.lexer.add("PAR_IZQ", r"\(")
        self.lexer.add("PAR_DER", r"\)")
        self.lexer.add("PUNTOYCOMA", r";")

        # Ignorar espacios, saltos de línea y comentarios
        self.lexer.ignore(r"\s+")
        self.lexer.ignore(r"#.*")

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
