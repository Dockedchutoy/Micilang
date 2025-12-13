"""
Python Micilang Queue Interpreter

Toto používá collections.deque objekt. Hodí se to.
Abych z deque měl pouze queue funkcionalitu, používám následující funkce:
 - append(x) - Přidá do deque objekt z pravé strany
 - clear() - Vrátí vyprázdněný deque
 - copy() - Vrátí kopii deque
 - extend(iterable) - Přídá do deque objekty z iteratovatelného objektu (seznamy, další deque atd)
 - popleft() - Odstraní z deque objekt z pravé strany
Z toho pouze append, extend a popleft nějak zvláštně manipulují s deque, a extend je jen append pro iterační objekty. Perfektní.
Navíc se dá použít queue[0], který nám vrátí příští objekty v řadě.
"""


import sys
from collections import deque

user_code = "var x = 1 * 2 + 6 / 2; // This is a comment //"

user_code = "var x = 0; if x == 1 {while true {printl 1;}} if x == 0 {printl 0;}"

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

        self.KEYWORDS = ["VAR", "PRINTL", "IF", "ELSEIF", "ELSE", "WHILE",         # Statementy
                "INPUT!", "NUM!",        # Funkce
                "TRUE", "FALSE", "NULL", "AND", "OR"]                       # Další speciální

        self.tokens = deque() # Veškeré tokeny
        self.chars = "" # momentální paměť
        self.cur = 0 # Pozice v kódu, kterou se zabývá lexer
        # code[self.cur] = CURrent position in CODE
    
    def peek(self): # --O kolik znaků se podívat dál?-- haha ted uz ne
        peeked = ""
        peek_cur = self.cur
        if self.cur < len(self.code):
            peek_cur += 1
            peeked += self.code[peek_cur]
        return peeked

    def gettokens(self):  # Pravý lexer

        # Chtěl bych říct, že všechno zde JE queue (podle mého názoru). Operace prováděné na řetězcích jdou zleva doprava, což je queueový.

        # Token: (Name, Object, Line)

        while self.cur < len(self.code):
    
            if self.code[self.cur].isalpha():         # Keywordy a identifikátory
                while self.cur < len(self.code) and self.code[self.cur].isalnum():
                    self.chars += self.code[self.cur]
                    self.cur += 1
                if self.chars.upper() in self.KEYWORDS:
                    self.tokens.append(deque([self.chars.upper(), self.chars]))
                else:
                    self.tokens.append(deque(["IDENTIFIER", self.chars]))
        
            elif self.code[self.cur].isnumeric():
                while self.cur < len(self.code) and self.code[self.cur].isnumeric():
                    self.chars += self.code[self.cur]
                    self.cur += 1
                self.tokens.append(deque(["NUMBER", int(self.chars)]))
            
            elif self.code[self.cur] == '"':        # Stringy
                self.cur += 1
                while self.cur < len(self.code) and self.code[self.cur] != '"':
                    self.chars += self.code[self.cur]
                    self.cur += 1
                self.cur += 1
                self.tokens.append(deque(["STRING", self.chars]))
    
            elif self.code[self.cur] == ";":          # Konec statementu
                self.tokens.append(deque(["SEMICOLON", ";"]))
                self.cur += 1
            
            elif self.code[self.cur] == "/":         # Komentáře / Děleno         
                if self.peek() == "/":
                    self.cur += 2
                    while self.cur < len(self.code) and "//" not in self.chars: 
                        self.cur += 1
                    self.cur += 1
                else:
                    self.tokens.append(deque(["SLASH", "/"]))
                    self.cur += 1
            
            elif self.code[self.cur] == "*":
                self.tokens.append(deque(["STAR", "*"]))
                self.cur += 1
    
            elif self.code[self.cur] == "=":
                if self.peek() == "=":
                    self.cur += 2
                    self.tokens.append(deque(["EQUAL_EQUAL", "=="]))
                else:
                    self.tokens.append(deque(["EQUAL", "="]))
                    self.cur += 1
            
            elif self.code[self.cur] == "!":
                if self.peek() == "=":
                    self.cur += 2
                    self.tokens.append(deque(["EXCL_EQUAL", "!="]))
                else:
                    self.tokens.append(deque(["EXCL", "!"]))
                    self.cur += 1
            
            elif self.code[self.cur] == ">":
                if self.peek() == "=":
                    self.cur += 2
                    self.tokens.append(deque(["GREAT_EQUAL", ">="]))
                else:
                    self.tokens.append(deque(["GREAT", ">"]))
                    self.cur += 1
            
            elif self.code[self.cur] == "<":
                if self.peek() == "=":
                    self.cur += 2
                    self.tokens.append(deque(["LESS_EQUAL", "<="]))
                else:
                    self.tokens.append(deque(["LESS", "<"]))
                    self.cur += 1
            
            elif self.code[self.cur] == "+":
                self.tokens.append(deque(["PLUS", "+"]))
                self.cur += 1
            
            elif self.code[self.cur] == "-":
                self.tokens.append(deque(["MINUS", "-"]))
                self.cur += 1
        
            elif self.code[self.cur] == "(":
                self.tokens.append(deque(["L_PARENS", "("]))
                self.cur += 1

            elif self.code[self.cur] == ")":
                self.tokens.append(deque(["R_PARENS", ")"]))
                self.cur += 1
            
            elif self.code[self.cur] == "{":
                self.tokens.append(deque(["L_BRACE", "{"]))
                self.cur += 1

            elif self.code[self.cur] == "}":
                self.tokens.append(deque(["R_BRACE", "}"]))
                self.cur += 1
        
            elif self.code[self.cur] == " " or self.code[self.cur] == "\n":
                self.cur += 1

            else: # Pro mezery/ostatní znaky ignorovat zatim
                error(self.cur, f"Invalid Character \"{self.code[self.cur]}\"")

            self.chars = ""
    
        self.tokens.append(deque(["EOF", None]))
        
        return self.tokens
    

# Parser


class CParserError(RuntimeError): pass

class Parser():
    def __init__(self, tokens):
        self.tokens = tokens # Full list of tokens

        # Vrácené parser tokeny musí být ve specifickém pořadí. První element musí vždy být typ tokenu.
    
    def error(self, token, message):
        error(token, message)
        return CParserError
    
    def peek(self):
        return self.tokens[0][0]
    
    def check(self, type):  # Shoduje se další token s tím co chceme?
        if self.peek() == "EOF": 
            return False
        return self.peek() == type

    def advance(self):  # Přesune se o další pozici/na následující token
        self.tokens[0].popleft()
        token = self.peek() # Kdyžtak by to mohlo být jen self.tokens[0]
        if self.peek() != "EOF":
            self.tokens.popleft()
        return token
    
    def match(self, *types):     # Pokud je další token to co chceme, pokračujeme na další pozici
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def expect(self, type, message):     # Pokud není další token to co chceme, máme problém. Jinak jdeme dál
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
        return deque(["Var", name, ini])
    
    def statement(self): # statement -> expressionStmt | ifStmt | printlStmt | block ;
        if self.check("R_BRACE"):
            return None
        
        if self.match("IF"):
            return self.ifStmt()
        elif self.match("WHILE"):
            return self.whileStmt()
        elif self.match("PRINTL"):
            return self.printlStmt()
        elif self.match("L_BRACE"):
            return deque(["Block", self.block()])
        return self.expressionStmt()
    
    def expressionStmt(self): # expressionStmt -> expression ";" ;
        expr = self.expression()
        self.expect("SEMICOLON", "Missing semicolon after expression")
        return deque(["ExpressionStmt", expr])
    
    def ifStmt(self): # ifStmt -> "if" expression block ("else" block)? ;
        condition = self.expression()
        self.expect("L_BRACE", "Missing \"{\" after if condition")
        thenBr = self.block()

        # IMPLEMENTOVAT ELSEIF

        elseBr = None
        if self.match("ELSE"):
            self.expect("L_BRACE", "Missing \"{\" after else condition")
            elseBr = self.block()
        return deque(["If", condition, thenBr, elseBr])
    
    def whileStmt(self): # ifStmt -> "while" expression block ;
        condition = self.expression()
        self.expect("L_BRACE", "Missing \"{\" after while condition")
        body = self.block()
        return deque(["While", condition, body])
    
    def printlStmt(self): # printlStmt -> "printl" expression ";" ;
        value = self.expression()
        self.expect("SEMICOLON", "Missing semicolon after value")
        return deque(["Printl", value])
    
    def block(self): # block -> "{" declaration* "}"
        stmts = deque()
        while not self.check("R_BRACE") and self.peek() != "EOF":
            stmt = self.declaration()
            if stmt is not None:
                stmts.append(stmt)
        self.expect("R_BRACE", "Missing \"}\" after block")
        return stmts
    
    def expression(self): # expression -> assignment;
        return self.assignment()
    
    def assignment(self):
        expr = self.logicOr()
        if self.match("EQUAL"): # equals? haha o tom jsem vůbec neslyšel neee neee
            val = self.assignment()

            if expr[0] == "Variable":
                expr.popleft() # Zbavuji se typu tokenu, zůstává nám jen jméno
                name = expr[0]
                return deque(["Assign", name, val])
            self.error(val, "Invalid target assignment")
        return expr
    
    def logicOr(self):
        expr = self.logicAnd()
        op = self.peek()
        while self.match("OR"):
            right = self.logicAnd()
            expr = deque(["Logical", expr, op, right])
        return expr
    
    def logicAnd(self):
        expr = self.equality()
        op = self.peek()
        while self.match("AND"):
            right = self.equality()
            expr = deque(["Logical", expr, op, right])
        return expr
    
    def equality(self):
        expr = self.comparison()
        op = self.peek()
        while self.match("EXCL_EQUAL", "EQUAL_EQUAL"):
            right = self.comparison()
            expr = deque(["Binary", expr, op, right])
        return expr
    
    def comparison(self):
        expr = self.term()
        op = self.peek()
        while self.match("GREAT", "GREAT_EQUAL", "LESS", "LESS_EQUAL"):
            right = self.term()
            expr = deque(["Binary", expr, op, right])
        return expr
    
    def term(self):
        expr = self.factor()
        op = self.peek()
        while self.match("PLUS", "MINUS"):
            right = self.factor()
            expr = deque(["Binary", expr, op, right])
        return expr
    
    def factor(self):
        expr = self.primary()
        op = self.peek()
        while self.match("STAR", "SLASH"):
            right = self.primary()
            expr = deque(["Binary", expr, op, right])
        return expr
    
    # IMPLEMENTOVAT UNÁRNÍ OPERACE
    
    def primary(self): # primary -> NUMBER | STRING | "true" | "false" | "null" | "(" expression ")" | IDENTIFIER ; 
        item = self.tokens[0]
        if self.match("NUMBER") or self.match("STRING"):
            return deque(["Literal", item[0]])
        
        elif self.match("TRUE"):
            return deque(["Literal", True])
        elif self.match("FALSE"):
            return deque(["Literal", False])
        elif self.match("NULL"):
            return deque(["Literal", None])

        elif self.match("L_PARENS"):
            expr = self.expression()
            self.expect("R_PARENS", "Missing \")\" after expression.")
            return deque(["Group", expr])
        
        elif self.match("IDENTIFIER"):
            return deque(["Variable", item])
        
        self.error(self.peek(), "Missing expression")
    
    # Main parsing function
    
    def parse(self):
        try:
            program = deque()

            while self.peek() != "EOF":
                program.append(self.declaration())

            return program
        
        except CParserError as e:
            return e

if __name__ == "__main__":
    hadError = False
    hadRuntimeError = False

    lexer = Lexer(user_code)
    lexer_out = (lexer.gettokens())
    print("LEXER OUTPUT: " + str(lexer_out))

    parser = Parser(lexer_out)
    parser_out = parser.parse()
    print("PARSER OUTPUT: " + str(parser_out))