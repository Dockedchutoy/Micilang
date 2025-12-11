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
                if self.peek() == "/":
                    self.cur += 2
                    while self.cur < len(self.code) and "//" not in self.chars: 
                        self.cur += 1
                    self.cur += 1
                else:
                    self.tokens.append(("SLASH", "/"))
                    self.cur += 1
            
            elif self.code[self.cur] == "*":
                self.tokens.append(("STAR", "*"))
                self.cur += 1
    
            elif self.code[self.cur] == "=":
                if self.peek() == "=":
                    self.cur += 2
                    self.tokens.append(("EQUAL_EQUAL", "=="))
                else:
                    self.tokens.append(("EQUAL", "="))
                    self.cur += 1
            
            elif self.code[self.cur] == "!":
                if self.peek() == "=":
                    self.cur += 2
                    self.tokens.append(("EXCL_EQUAL", "!="))
                else:
                    self.tokens.append(("EXCL", "!"))
                    self.cur += 1
            
            elif self.code[self.cur] == ">":
                if self.peek() == "=":
                    self.cur += 2
                    self.tokens.append(("GREAT_EQUAL", ">="))
                else:
                    self.tokens.append(("GREAT", ">"))
                    self.cur += 1
            
            elif self.code[self.cur] == "<":
                if self.peek() == "=":
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
    

# Parser


class CParserError(RuntimeError): pass

class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur = 0
    
    def error(self, token, message):
        error(token, message)
        return CParserError

    def parse(self):
        program = deque()

        while not self.tokens[0][0] == "EOF":
            program.append()
        
        return program

if __name__ == "__main__":
    hadError = False
    hadRuntimeError = False

    lexer = Lexer(user_code)
    lexer_out = (lexer.gettokens())
    print("LEXER OUTPUT: " + str(lexer_out))

    parser = Parser(lexer_out)
    parser_out = parser.parse()
    print("PARSER OUTPUT: " + str(parser_out))