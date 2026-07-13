from rply import ParserGenerator

from .ast import Arbol


class SymbolTable(dict):
    """Diccionario de símbolos que también conserva declaraciones repetidas."""

    def __init__(self):
        super().__init__()
        self.duplicate_declarations = []

    def register(self, name, data_type):
        if name in self:
            self.duplicate_declarations.append(
                {
                    "name": name,
                    "original_type": self[name],
                    "repeated_type": data_type,
                }
            )
            return

        self[name] = data_type


class Parser:
    """Construye el AST de un programa escrito en Cascabel."""

    TOKENS = [
        "PROGRAMA",
        "SINO",
        "MIENTRAS",
        "SI",
        "ENTONCES",
        "PARA",
        "DESDE",
        "HASTA",
        "OP_LECTURA",
        "OP_ESCRITURA",
        "TIPO",
        "LIT_CADENA",
        "LIT_REAL",
        "LIT_ENTERO",
        "LIT_BOOL",
        "OP_COMP",
        "OP_ASIGN",
        "OP_SUMA",
        "OP_RESTA",
        "OP_MULT",
        "OP_DIV",
        "OP_NOT",
        "OP_Y",
        "OP_O",
        "ID",
        "LLAV_ABRE",
        "LLAV_CIERRA",
        "PAR_IZQ",
        "PAR_DER",
        "PUNTOYCOMA",
    ]

    def __init__(self):
        self.pg = ParserGenerator(self.TOKENS)
        self.symbols = SymbolTable()

    def parse(self):
        # Programa y bloques
        @self.pg.production("programa : PROGRAMA bloque")
        def programa(p):
            return Arbol("programa", p[1])

        @self.pg.production("bloque : LLAV_ABRE instrucciones LLAV_CIERRA")
        def bloque_con_instrucciones(p):
            return p[1]

        @self.pg.production("bloque : LLAV_ABRE LLAV_CIERRA")
        def bloque_vacio(_p):
            return []

        @self.pg.production("instrucciones : instruccion instrucciones")
        @self.pg.production("instrucciones : instruccion")
        def instrucciones(p):
            if len(p) == 2:
                return [p[0]] + p[1]
            return [p[0]]

        @self.pg.production("instruccion : escritura")
        @self.pg.production("instruccion : lectura")
        @self.pg.production("instruccion : declaracion")
        @self.pg.production("instruccion : asignacion")
        @self.pg.production("instruccion : condicion")
        @self.pg.production("instruccion : mientras")
        @self.pg.production("instruccion : para")
        def instruccion(p):
            return p[0]

        # Entrada y salida
        @self.pg.production("escritura : OP_ESCRITURA expresion PUNTOYCOMA")
        def escritura(p):
            return Arbol("escribe", [p[1]])

        @self.pg.production("lectura : OP_LECTURA ID PUNTOYCOMA")
        def lectura(p):
            return Arbol("lee", [p[1].value])

        # Declaraciones y asignaciones
        @self.pg.production("declaracion : TIPO ID PUNTOYCOMA")
        @self.pg.production(
            "declaracion : TIPO ID OP_ASIGN expresion PUNTOYCOMA"
        )
        def declaracion(p):
            data_type = p[0].value
            name = p[1].value
            self.symbols.register(name, data_type)

            if len(p) == 3:
                return Arbol("declara", [data_type, name])

            return Arbol("declara_asigna", [data_type, name, p[3]])

        @self.pg.production("asignacion : ID OP_ASIGN expresion PUNTOYCOMA")
        def asignacion(p):
            return Arbol("=", [p[0].value, p[2]])

        # Condicionales. La gramática está factorizada para que el parser
        # no tenga que decidir prematuramente entre 'si' y 'si ... sino'.
        @self.pg.production(
            "condicion : SI condicion_encabezado ENTONCES bloque sino_opcional"
        )
        def condicion(p):
            condition = p[1]
            then_block = p[3]
            else_block = p[4]

            if else_block is None:
                return Arbol("si", [condition] + then_block)

            return Arbol("si_sino", [condition, then_block, else_block])

        @self.pg.production("condicion_encabezado : expresion")
        def condicion_encabezado(p):
            # Los paréntesis ya forman parte de la gramática de expresiones.
            return p[0]

        @self.pg.production("sino_opcional : SINO bloque")
        def sino_presente(p):
            return p[1]

        @self.pg.production("sino_opcional :")
        def sino_ausente(_p):
            return None

        # Ciclos
        @self.pg.production("mientras : MIENTRAS condicion_encabezado bloque")
        def mientras(p):
            return Arbol("mientras", [p[1], p[2]])

        @self.pg.production(
            "para : PARA ID DESDE expresion HASTA expresion bloque"
        )
        def para(p):
            return Arbol("para", [p[1].value, p[3], p[5], p[6]])

        # Expresiones: de menor a mayor precedencia.
        @self.pg.production("expresion : expresion_o")
        def expresion(p):
            return p[0]

        @self.pg.production("expresion_o : expresion_o OP_O expresion_y")
        def expresion_o(p):
            return Arbol("o", [p[0], p[2]])

        @self.pg.production("expresion_o : expresion_y")
        def expresion_o_simple(p):
            return p[0]

        @self.pg.production("expresion_y : expresion_y OP_Y comparacion")
        def expresion_y(p):
            return Arbol("y", [p[0], p[2]])

        @self.pg.production("expresion_y : comparacion")
        def expresion_y_simple(p):
            return p[0]

        @self.pg.production("comparacion : suma OP_COMP suma")
        def comparacion(p):
            return Arbol(p[1].value, [p[0], p[2]])

        @self.pg.production("comparacion : suma")
        def comparacion_simple(p):
            return p[0]

        @self.pg.production("suma : suma OP_SUMA producto")
        @self.pg.production("suma : suma OP_RESTA producto")
        def suma(p):
            return Arbol(p[1].value, [p[0], p[2]])

        @self.pg.production("suma : producto")
        def suma_simple(p):
            return p[0]

        @self.pg.production("producto : producto OP_MULT unaria")
        @self.pg.production("producto : producto OP_DIV unaria")
        def producto(p):
            return Arbol(p[1].value, [p[0], p[2]])

        @self.pg.production("producto : unaria")
        def producto_simple(p):
            return p[0]

        @self.pg.production("unaria : OP_NOT unaria")
        def negacion_booleana(p):
            return Arbol("no", [p[1]])

        @self.pg.production("unaria : OP_RESTA unaria")
        def negacion_numerica(p):
            return Arbol("negativo", [p[1]])

        @self.pg.production("unaria : primario")
        def unaria_simple(p):
            return p[0]

        @self.pg.production("primario : valor")
        def primario_valor(p):
            return p[0]

        @self.pg.production("primario : PAR_IZQ expresion PAR_DER")
        def primario_parentesis(p):
            return p[1]

        @self.pg.production("valor : LIT_CADENA")
        @self.pg.production("valor : LIT_ENTERO")
        @self.pg.production("valor : LIT_REAL")
        @self.pg.production("valor : LIT_BOOL")
        @self.pg.production("valor : ID")
        def valor(p):
            return p[0].value

        @self.pg.error
        def error_handle(token):
            if token is None or token.gettokentype() == "$end":
                message = (
                    "ERROR SINTÁCTICO: el programa terminó inesperadamente; "
                    "revise llaves, paréntesis y puntos y coma."
                )
                print(f"\033[91m{message}\033[0m")
                raise ValueError(message)

            position = token.getsourcepos()
            line = position.lineno if position is not None else "desconocida"
            column = position.colno if position is not None else "desconocida"
            message = (
                f"ERROR SINTÁCTICO: no se esperaba '{token.value}' "
                f"en la línea {line}, columna {column}."
            )
            print(f"\033[91m{message}\033[0m")
            raise ValueError(message)

    def get_symbols(self):
        return self.symbols

    def get_parser(self):
        return self.pg.build()
