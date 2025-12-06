"""
Micilang Python Interpreter

https://craftinginterpreters.com/scanning.html <- veliky dobry

TODO:
        
    udělat parser
    ehm ehm jo
"""

import sys

# Získání kódu

user_code = 'var x = 1 * 2 + 6 / 2; // 5\nprintl x;'      # Tady půjde Micilang kód. Soubory a shell vymyslím později.

user_code = 'var x = 2; var y = 2; printl x + y;'

# Error reporting

def error(position, message):
    report(position, "", message)

def report(position, item, message):
    print(f"[{position}] Error {item}: {message}")
    hadError = True

def runtimeError(error):
    print(f"[{error.token}] {error.message}")
    hadRuntimeError = True


# Lexer


class Lexer():
    def __init__(self, code): # Lexer setup

        self.code = code

        self.KEYWORDS = ["VAR", "PRINTL", "IF!", "ELSEIF!", "ELSE!", "FUNC!", "WHILE!",         # Statementy
                "INPUT!", "NUM!",        # Funkce
                "TRUE", "FALSE", "NULL"]                       # Další speciální

        self.tokens = [] # Veškeré tokeny
        self.chars = "" # momentální paměť
        self.cur = 0 # Pozice, kterou se zabývá lexer
        # code[self.cur] = CURrent position in CODE
    
    def peek(self, n): # O kolik znaků se podívat dál?
        peeked = ""
        peek_cur = self.cur
        while self.cur < len(self.code) and len(peeked) < n:
            peek_cur += 1
            peeked += self.code[peek_cur]
        return peeked

    def gettokens(self):  # Pravý lexer

        # Token: (Name, Object, Line)

        while self.cur < len(self.code):
    
            if self.code[self.cur].isalpha():         # Keywordy a identifikátory
                while self.cur < len(self.code) and self.code[self.cur].isalnum():
                    self.chars += self.code[self.cur]
                    self.cur += 1
                if self.chars.upper() in self.KEYWORDS:
                    self.tokens.append((self.chars.upper(), self.chars))
                else:
                    self.tokens.append(("IDENTIFIER", self.chars))
        
            elif self.code[self.cur].isnumeric():
                while self.cur < len(self.code) and self.code[self.cur].isnumeric():
                    self.chars += self.code[self.cur]
                    self.cur += 1
                self.tokens.append(("NUMBER", int(self.chars)))
            
            elif self.code[self.cur] == '"':        # Stringy
                self.cur += 1
                while self.cur < len(self.code) and self.code[self.cur] != '"':
                    self.chars += self.code[self.cur]
                    self.cur += 1
                self.cur += 1
                self.tokens.append(("STRING", self.chars))
    
            elif self.code[self.cur] == ";":          # Konec statementu
                self.tokens.append(("SEMICOLON", ";"))
                self.cur += 1
            
            elif self.code[self.cur] == "/":         # Komentáře / Děleno
                if self.peek(1) == "/":
                    self.cur += 2
                    while self.cur < len(self.code) and self.code[self.cur] != "\n": self.cur += 1
                else: #NEZAPOMENOUT TO UDĚLAT I PRO /// !!!!!!
                    self.tokens.append(("SLASH", "/"))
                    self.cur += 1
            
            elif self.code[self.cur] == "*":
                self.tokens.append(("STAR", "*"))
                self.cur += 1
    
            elif self.code[self.cur] == "=":
                self.tokens.append(("EQUAL", "="))
                self.cur += 1
            
            elif self.code[self.cur] == "+":
                self.tokens.append(("PLUS", "+"))
                self.cur += 1
        
            elif self.code[self.cur] == "(":
                self.tokens.append(("L_PARENS", "("))
                self.cur += 1

            elif self.code[self.cur] == ")":
                self.tokens.append(("R_PARENS", ")"))
                self.cur += 1
        
            elif self.code[self.cur] == " " or self.code[self.cur] == "\n":
                self.cur += 1

            else: # Pro mezery/ostatní znaky ignorovat zatim
                error(self.cur, f"Invalid Character \"{self.code[self.cur]}\"")

            self.chars = ""
    
        self.tokens.append(("EOF", None))
        
        return self.tokens


# Parser Visitor Classes (ano)


class Expr():
    pass

class Literal(Expr):    # val
    def __init__(self, val):
        self.val = val
    
    def __str__(self):
        if self.val == None:
            return "null"
        elif self.val == True:
            return "true"
        elif self.val == True:
            return "false"
        return f"{self.val}"

    def accept(self, visitor):
        return visitor.visitLiteral(self)

class Group(Expr):      # (expression)
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return f"Group({self.expression})"

    def accept(self, visitor):
        return visitor.visitGroup(self)

class Binary(Expr):     # left operator right
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"Binary({self.left}, {self.operator}, {self.right})"
    
    def accept(self, visitor):
        return visitor.visitBinary(self)

class Variable(Expr):     # Printl expression;
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Variable({self.name})"

    def accept(self, visitor):
        return visitor.visitVariable(self)

class Assign(Expr):
    def __init__(self, name, val):
        self.name = name
        self.val = val
    
    def __str__(self):
        return f"Assign_{self.name}({self.val})"

    def accept(self, visitor):
        return visitor.visitAssign(self)

class Stmt():
    pass

class Expression(Stmt):     # expression
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return f"Expression({self.expression})"

    def accept(self, visitor):
        return visitor.visitExpression(self)

class Printl(Stmt):     # Printl expression;
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return f"Printl({self.expression})"

    def accept(self, visitor):
        return visitor.visitPrintl(self)
    
class Var(Stmt):     # Printl expression;
    def __init__(self, name, ini):
        self.name = name
        self.ini = ini
    
    def __str__(self):
        return f"Var_{self.name}({self.ini})"

    def accept(self, visitor):
        return visitor.visitVar(self)


# Parser (asi se zastřelim)


class CParserError(RuntimeError): pass

class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur = 0
    
    def error(self, token, message):
        error(token, message)
        return CParserError
    
    def sync(self):
        self.advance()

        while self.peek()[0] != "EOF":
            if self.previous()[0] == "SEMICOLON":
                return None
            match self.peek()[0]:
                case "VAR" | "WRITE":
                    return None
            self.advance()
    
    def peek(self): # Získá současný token
        return self.tokens[self.cur]

    def previous(self): # Získá předchozí token
        return self.tokens[self.cur - 1]
    
    def advance(self):  # Přesune se o další pozici
        if self.peek()[0] != "EOF":
            self.cur += 1
        return self.previous()
    
    def check(self, type):  # Shoduje se další token s tím co chceme?
        if self.peek()[0] == "EOF": 
            return False
        return self.peek()[0] == type
    
    def match(self, *types):     # Pokud je další token to co chceme, pokračujeme 
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def expect(self, type, message):     # Pokud není další token to co chceme, máme problém
        if self.check(type):
            return self.advance()
        
        self.error(self.peek(), message)
    
    def declaration(self):  # declaration -> varDeclaration | statement
        try:
            if self.match("VAR"):
                return self.varDeclaration()
            return self.statement()
        except CParserError as e:
            print("o shit")
            self.sync()
            return None
        
    def varDeclaration(self): # varDeclaration -> "var" IDENTIFIER ( "=" expression )? ";" ;
        name = self.expect("IDENTIFIER", "Missing variable name")
        ini = None
        if self.match("EQUAL"):
            ini = self.expression()
        self.expect("SEMICOLON", "Missing semicolon after declaration")
        return Var(name, ini)
    
    def statement(self): # statement -> expressionStmt | printlStmt ;
        if self.match("PRINTL"):
            return self.printlStmt()
        return self.expressionStmt()
    
    def expressionStmt(self): # expressionStmt -> expression ";" ;
        expr = self.expression()
        self.expect("SEMICOLON", "Missing semicolon after expression")
        return Expression(expr)
    
    def printlStmt(self): # printlStmt -> "printl" expression ";" ;
        value = self.expression()
        self.expect("SEMICOLON", "Missing semicolon after value")
        return Printl(value)
    
    def expression(self): # expression -> assignment;
        return self.assignment()
    
    def assignment(self):
        expr = self.equality()
        if self.match("EQUAL"):
            equals = self.previous()
            val = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, val)
            self.error(equals, "Invalid target assignment")
        return expr

    def term(self): # term -> factor ( ( "-" | "+" ) factor )* ;
        expr = self.factor()
        while self.match("PLUS", "MINUS"):
            op = self.previous()
            right = self.factor()
            expr = Binary(expr, op[0], right)
        return expr

    def factor(self): # factor -> primary ( ( "/" | "*" ) primary )* ;
        expr = self.primary()
        while self.match("STAR", "SLASH"):
            op = self.previous()
            right = self.primary()
            expr = Binary(expr, op[0], right)
        return expr

    def primary(self): # primary -> NUMBER | STRING | "true" | "false" | "null" | "(" expression ")" | IDENTIFIER ;
        if self.match("NUMBER") or self.match("STRING"):
            return Literal(self.previous()[1])
        
        elif self.match("TRUE"):
            return Literal(True)
        elif self.match("FALSE"):
            return Literal(False)
        elif self.match("NULL"):
            return Literal(None)

        elif self.match("L_PARENS"):
            expr = self.expression()
            self.expect("R_PARENS", "Missing \")\" after expression.")
            return Group(expr)
        
        elif self.match("IDENTIFIER"):
            return Variable(self.previous())
        
        self.error(self.peek(), "Missing expression")
    
    def parse(self):    # Hlavní funkce
        try:
            program = []

            while self.peek()[0] != "EOF":
                program.append(self.declaration())

            return program
        
        except CParserError as e:
            return e


# Environment (pro interpretík :3)


class Environment():
    def __init__(self):
        self.vals = {} 
    
    def create(self, name, val):
        self.vals[name] = val
    
    def retrieve(self, name):
        if name[1] in self.vals:
            return self.vals[name[1]]
        
        raise CRuntimeError(name, f"Undefined variable \"{name[1]}\"")
    
    def assign(self, name, val):
        if name[1] in self.vals:
            self.vals[name] = val
            return
        
        raise CRuntimeError(name, f"Undefined variable {name[1]}")


# Interpreter


class CRuntimeError(RuntimeError):
    def __init__(self, token, message, *args):
        self.message = message
        self.token = token
        super().__init__(*args)


class Interpreter():
    def __init__(self):
        self.env = Environment()

    def checkNumOp(self, operator, operand):
        if isinstance(operand, float):
            return None
        raise CRuntimeError(operator, "Invalid operand type.")
    
    def checkNumOps(self, left, operator, right):
        if isinstance(left, float) and isinstance(right, float):
            return None
        raise CRuntimeError(operator, "Invalid operands type.")

    def evaluate(self, expr):       # Přesune nás zase na interpretu visitor
        return expr.accept(self)

    def execute(self, stmt):
        return stmt.accept(self)

    # Statement visitors

    def visitExpression(self, stmt):    # já nevim
        self.evaluate(stmt.expression)
        return None

    def visitPrintl(self, stmt):    # Příkaz printl
        value = self.evaluate(stmt.expression)
        
        if value == None:
            print("null")
        elif value == True:
            print("true")
        elif value == False:
            print("false")
        else:
            print(value)
    
    def visitVar(self, stmt):   # příkaz var
        val = None
        if not stmt.ini == None:
            val = self.evaluate(stmt.ini)
        self.env.create(stmt.name[1], val)
        return None
    
    # Expression visitors
    
    def visitLiteral(self, expr):   # Čísla, řetězce, booleany
        return expr.val

    def visitGroup(self, expr):     # ( )
        return self.evaluate(expr.expression)

    def visitBinary(self, expr):       # Binární operace
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator:
            case "PLUS":
                if isinstance(left, float) and isinstance(right, float) or isinstance(left, int) and isinstance(right, int):  # Sčítání čísel.
                    return float(left + right)
                elif isinstance(left, str) and isinstance(right, str):  # Sčítání řetězců
                    return str(left + right)

                # error check here

            case "MINUS":
                # error check here
                return float(left - right)

            case "STAR":
                # error check here
                return float(left * right)
            
            case "SLASH":
                # error check here
                return float(left / right)
    
    def visitVariable(self, expr):
        return self.env.retrieve(expr.name)
    
    def visitAssign(self, expr):
        val = self.evaluate(expr.val)
        self.env.assign(expr.name, val)
        return val
    
    # Interpretting function
    
    def interpret(self, program):
        try:
            for statement in program:
                self.execute(statement)
        except CRuntimeError as e:
            runtimeError(e)


# Hl. loop


if __name__ == "__main__":
    hadError = False
    hadRuntimeError = False

    try:
        if not sys.argv[1].endswith(".mcl"): print("Warning: File does not have Micilang file extension.")
        with open(sys.argv[1], encoding="utf_8") as f:  # Python asi nepoznává, co je kurva .mcl, tak musíme to donutit do utf-8. Kdyby byl encoding jinej, bylo by zle, ale... kdo by kurva nepoužíval utf-8??
            user_code = f.read()
    except IndexError as e:
        print("Micilang Terminal Mode")


    lexer = Lexer(user_code)
    lexer_out = (lexer.gettokens())
    print("LEXER OUTPUT: " + str(lexer_out))

    parser = Parser(lexer_out)
    parser_out = parser.parse()
    print("PARSER OUTPUT: " + str(parser_out))

    interpreter = Interpreter()
    interpreter.interpret(parser_out)