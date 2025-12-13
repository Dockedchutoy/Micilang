"""
Micilang Python Interpreter

https://craftinginterpreters.com/scanning.html <- veliky dobry

TODO:
        
    udělat parser
    ehm ehm jo
"""

import sys
from collections import deque

# Získání kódu

user_code = 'var x = 1 * 2 + 6 / 2; // 5\nprintl x;'      # Tady půjde Micilang kód. Soubory a shell vymyslím později.

user_code = 'var x = 2; var y = 2; printl x + y;'

user_code = 'var x = 1; if x == 1 {while true {printl x;}} else {printl x;}'

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

        self.KEYWORDS = ["VAR", "PRINTL", "IF", "ELSEIF", "ELSE", "FUNC!", "WHILE",         # Statementy
                "INPUT!", "NUM!",        # Funkce
                "TRUE", "FALSE", "NULL", "AND", "OR"]                       # Další speciální

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
                if self.peek(2) == "//":
                    self.cur += 3
                    while self.cur < len(self.code) and "///" not in self.chars:
                            self.chars += self.code[self.cur]
                            self.cur += 1
                    self.cur += 1
                
                elif self.peek(1) == "/":
                    self.cur += 2
                    while self.cur < len(self.code) and self.code[self.cur] != "\n": self.cur += 1
                else: #NEZAPOMENOUT TO UDĚLAT I PRO /// !!!!!!
                      # dw už to tam je
                    self.tokens.append(("SLASH", "/"))
                    self.cur += 1
            
            elif self.code[self.cur] == "*":
                self.tokens.append(("STAR", "*"))
                self.cur += 1
    
            elif self.code[self.cur] == "=":
                if self.peek(1) == "=":
                    self.cur += 2
                    self.tokens.append(("EQUAL_EQUAL", "=="))
                else:
                    self.tokens.append(("EQUAL", "="))
                    self.cur += 1
            
            elif self.code[self.cur] == "!":
                if self.peek(1) == "=":
                    self.cur += 2
                    self.tokens.append(("EXCL_EQUAL", "!="))
                else:
                    self.tokens.append(("EXCL", "!"))
                    self.cur += 1
            
            elif self.code[self.cur] == ">":
                if self.peek(1) == "=":
                    self.cur += 2
                    self.tokens.append(("GREAT_EQUAL", ">="))
                else:
                    self.tokens.append(("GREAT", ">"))
                    self.cur += 1
            
            elif self.code[self.cur] == "<":
                if self.peek(1) == "=":
                    self.cur += 2
                    self.tokens.append(("LESS_EQUAL", "<="))
                else:
                    self.tokens.append(("LESS", "<"))
                    self.cur += 1
            
            elif self.code[self.cur] == "+":
                self.tokens.append(("PLUS", "+"))
                self.cur += 1
            
            elif self.code[self.cur] == "-":
                self.tokens.append(("MINUS", "-"))
                self.cur += 1
        
            elif self.code[self.cur] == "(":
                self.tokens.append(("L_PARENS", "("))
                self.cur += 1

            elif self.code[self.cur] == ")":
                self.tokens.append(("R_PARENS", ")"))
                self.cur += 1
            
            elif self.code[self.cur] == "{":
                self.tokens.append(("L_BRACE", "{"))
                self.cur += 1

            elif self.code[self.cur] == "}":
                self.tokens.append(("R_BRACE", "}"))
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
    
    def __repr__(self):
        if self.val == None:
            return "null"
        elif self.val == True and isinstance(self.val, bool):
            return "true"
        elif self.val == False and isinstance(self.val, bool):
            return "false"
        return f"{self.val}"

    def accept(self, visitor):
        return visitor.visitLiteral(self)

class Group(Expr):      # (expression)
    def __init__(self, expression):
        self.expression = expression
    
    def __repr__(self):
        return f"Group({self.expression})"

    def accept(self, visitor):
        return visitor.visitGroup(self)

class Logical(Expr):      # and | or
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return f"Logic({self.left}, {self.operator} , {self.right})"

    def accept(self, visitor):
        return visitor.visitLogical(self)

class Binary(Expr):     # left operator right
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return f"Binary({self.left}, {self.operator}, {self.right})"
    
    def accept(self, visitor):
        return visitor.visitBinary(self)

class Unary(Expr):     # operator right
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return f"Unary({self.operator}, {self.right})"
    
    def accept(self, visitor):
        return visitor.visitUnary(self)

class Variable(Expr):     # Printl expression;
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Variable({self.name})"

    def accept(self, visitor):
        return visitor.visitVariable(self)

class Assign(Expr):
    def __init__(self, name, val):
        self.name = name
        self.val = val
    
    def __repr__(self):
        return f"Assign_{self.name}({self.val})"

    def accept(self, visitor):
        return visitor.visitAssign(self)

class Stmt():
    pass

class Expression(Stmt):     # expression
    def __init__(self, expression):
        self.expression = expression
    
    def __repr__(self):
        return f"Expression({self.expression})"

    def accept(self, visitor):
        return visitor.visitExpression(self)

class If(Stmt):     # Printl expression;
    def __init__(self, condition, thenBr, elseBr):
        self.condition = condition
        self.thenBr = thenBr
        self.elseBr = elseBr
    
    def __repr__(self):
        return f"If {self.condition}:({self.thenBr}), else ({self.thenBr})"

    def accept(self, visitor):
        return visitor.visitIf(self)

class Printl(Stmt):     # Printl expression;
    def __init__(self, expression):
        self.expression = expression
    
    def __repr__(self):
        return f"Printl({self.expression})"

    def accept(self, visitor):
        return visitor.visitPrintl(self)
    
class Var(Stmt):     # variable declaration expression;
    def __init__(self, name, ini):
        self.name = name
        self.ini = ini
    
    def __repr__(self):
        return f"Var_{self.name}({self.ini})"

    def accept(self, visitor):
        return visitor.visitVar(self)
    
class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"While {self.condition}({self.body})"

    def accept(self, visitor):
        return visitor.visitWhile(self)

class Block(Stmt):     # block of code;
    def __init__(self, stmts):
        self.stmts = stmts
    
    def __repr__(self):
        return f"Block({self.stmts})"

    def accept(self, visitor):
        return visitor.visitBlock(self)


# Parser (asi se zastřelim)


class CParserError(RuntimeError): pass

class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur = 0
    
    def error(self, token, message):
        error(token, message)
        raise CParserError
    
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
    
    def advance(self):  # Přesune se o další pozici/na následující token
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

    # real shit
    
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
    
    def statement(self): # statement -> expressionStmt | ifStmt | printlStmt | block ;
        if self.match("IF"):
            return self.ifStmt()
        elif self.match("WHILE"):
            return self.whileStmt()
        elif self.match("PRINTL"):
            return self.printlStmt()
        elif self.match("L_BRACE"):
            return Block(self.block())
        return self.expressionStmt()
    
    def expressionStmt(self): # expressionStmt -> expression ";" ;
        expr = self.expression()
        self.expect("SEMICOLON", "Missing semicolon after expression")
        return Expression(expr)
    
    def ifStmt(self): # ifStmt -> "if" expression block ("else" block)? ;
        condition = self.expression()
        self.expect("L_BRACE", "Missing \"{\" after if condition")
        thenBr = self.block()

        # IMPLEMENTOVAT ELSEIF

        elseBr = None
        if self.match("ELSE"):
            self.expect("L_BRACE", "Missing \"{\" after else condition")
            elseBr = self.block()
        return If(condition, thenBr, elseBr)
    
    def whileStmt(self): # ifStmt -> "while" expression block ;
        condition = self.expression()
        self.expect("L_BRACE", "Missing \"{\" after while condition")
        body = self.block()
        return While(condition, body)
    
    def printlStmt(self): # printlStmt -> "printl" expression ";" ;
        value = self.expression()
        self.expect("SEMICOLON", "Missing semicolon after value")
        return Printl(value)
    
    def block(self): # block -> "{" declaration* "}"
        statements = []
        while not self.check("R_BRACE") and self.peek()[0] != "EOF":
            statements.append(self.declaration())
        self.expect("R_BRACE", "Missing \"}\" after block")
        return statements
    
    def expression(self): # expression -> assignment;
        return self.assignment()
    
    def assignment(self):
        expr = self.logicOr()
        if self.match("EQUAL"):
            equals = self.previous()
            val = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, val)
            self.error(equals, "Invalid target assignment")
        return expr
    
    def logicOr(self):
        expr = self.logicAnd()
        while self.match("OR"):
            op = self.previous()
            right = self.logicAnd()
            expr = Logical(expr, op, right)
        return expr
    
    def logicAnd(self):
        expr = self.equality()
        while self.match("AND"):
            op = self.previous()
            right = self.equality()
            expr = Logical(expr, op, right)
        return expr
    
    def equality(self):
        expr = self.comparison()
        while self.match("EXCL_EQUAL", "EQUAL_EQUAL"):
            op = self.previous()
            right = self.comparison()
            expr = Binary(expr, op[0], right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match("GREAT", "GREAT_EQUAL", "LESS", "LESS_EQUAL"):
            op = self.previous()
            right = self.term()
            expr = Binary(expr, op[0], right)
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
    
    def unary(self):
        if self.match("EXCL", "MINUS"):
            op = self.previous()
            right = self.unary()
            return Unary(op, right)

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
    
    # Hlavní funkce
    
    def parse(self):
        try:
            program = []

            while self.peek()[0] != "EOF":
                program.append(self.declaration())

            return program
        
        except CParserError as e:
            return e


# Environment (pro interpretík :3)


class Environment():
    def __init__(self, enclosing=None):
        self.vals = {} 
        self.enclosing = enclosing
    
    def create(self, name, val):
        self.vals[name] = val
    
    def retrieve(self, name):
        if name[1] in self.vals:
            return self.vals[name[1]]

        if not self.enclosing == None:
                return self.enclosing.retrieve(name)
        
        raise CRuntimeError(name, f"Undefined variable \"{name[1]}\"")
    
    def assign(self, name, val):
        if name[1] in self.vals:
            self.vals[name] = val
            return

        if not self.enclosing == None:
                self.enclosing.assign(name, val)
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

    def isTrue(self, object):
        if object == None:
            return False
        elif isinstance(object, bool):
            return bool(object)
        elif object == "":
            return False
        elif object < 1:
            return False
        return True
    
    def isEqual(self, left, right):
        if left == None and right == None:
            return True
        elif left == None:
            return False
        return left == right

    # Statement visitors

    def visitExpression(self, stmt):    # já nevim
        self.evaluate(stmt.expression)
        return None
    
    def visitIf(self, stmt):
        if self.isTrue(self.evaluate(stmt.condition)):
            self.execBlock(stmt.thenBr, Environment(self.env))
        elif stmt.elseBr != None:
            self.execBlock(stmt.elseBr, Environment(self.env))
        return None
    
    def visitWhile(self, stmt):
        while self.isTrue(self.evaluate(stmt.condition)):
            self.execBlock(stmt.body, Environment(self.env))
        return None

    def visitPrintl(self, stmt):    # Příkaz printl
        value = self.evaluate(stmt.expression)
        
        if value == None:
            print("null")
        elif value == True and isinstance(value, bool):
            print("true")
        elif value == False and isinstance(value, bool):
            print("false")
        else:
            print(value)
    
    def visitVar(self, stmt):   # příkaz var
        val = None
        if not stmt.ini == None:
            val = self.evaluate(stmt.ini)
        self.env.create(stmt.name[1], val)
        return None
    
    def visitBlock(self, stmt):
        self.execBlock(stmt.stmts, Environment(self.env))
        return None
    
    def execBlock(self, stmts, env):
        previous = self.env
        try:
            self.env = env

            for stmt in stmts:
                self.execute(stmt)
        finally:
            self.env = previous
    
    # Expression visitors
    
    def visitLiteral(self, expr):   # Čísla, řetězce, booleany
        return expr.val

    def visitGroup(self, expr):     # ( )
        return self.evaluate(expr.expression)
    
    def visitUnary(self, expr):
        right = self.evaluate(expr.right)

        match self.operator:
            case "MINUS":
                return -float(right)
            case "EXCL":
                return not self.isTrue(right)
            
        return None
    
    def visitLogical(self, expr):
        left = self.evaluate(expr.left)

        if expr.operator == "OR":
            if self.isTrue(left):
                return left
        else:
            if not self.isTrue(self):
                return left
        return self.evaluate(expr.right)

    def visitBinary(self, expr):       # Binární operace
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator:
            case "PLUS":
                if isinstance(left, float) and isinstance(right, float) or isinstance(left, int) and isinstance(right, int):  # Sčítání čísel.
                    return float(left + right)
                elif isinstance(left, str) and isinstance(right, str):  # Sčítání řetězců
                    return str(left + right)

                # error check here. Tahle celá věc závisí na tom že budeš porovnávat čísla. Jinak se zastřel.

            case "MINUS":
                # error check here
                return float(left - right)

            case "STAR":
                # error check here
                return float(left * right)
            
            case "SLASH":
                # error check here
                return float(left / right)
            
            case "GREAT":
                return left > right
            
            case "GREAT_EQUAL":
                return left >= right
            
            case "LESS":
                return left < right
            
            case "LESS_EQUAL":
                return left <= right
            
            case "EXCL_EQUAL":
                return not self.isEqual(left, right)
            
            case "EQUAL_EQUAL":
                return self.isEqual(left, right)
    
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
        except KeyboardInterrupt:
            print("EXECUTION INTERRUPTED BY USER")


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
    print("PARSER OUTPUT: " + repr(parser_out))

    interpreter = Interpreter()
    interpreter.interpret(parser_out)
