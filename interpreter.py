"""
Micilang Python Interpreter

https://craftinginterpreters.com/scanning.html <- veliky dobry

TODO:
    dodělat lexer
        trochu poklidit ať je to hezky (ale nemusim)
        udelat keywaordy jaksepatri
        
    udělat parser
    ehm ehm jo

Grammer:

expression -> term SEMICOLON;
term -> factor ( ( "-" | "+" ) factor )* ;
factor -> primary ( ( "/" | "*" ) primary )* ;
primary -> NUMBER | STRING | "true" | "false" | "null" | "(" expression ")" ;

operation -> statement operator statement
"""

# Získání kódu

user_code = 'var x = 1 + 6 / 2; // This is a comment\nwrite(x);'      # Tady půjde Micilang kód. Soubory a shell vymyslím později.

user_code = "1 * 2 + 6 / 2; // 5"

# Queue object

class Queue():
    pass

# Error reporting

def error(position, message):
    return f"ERROR AT {position}: {message}."


# Lexer

class Lexer():
    def __init__(self, code): # Lexer setup

        self.code = code

        self.KEYWORDS = ["VAR", "PRINT",         # Statementy
                "INPUT"        # Funkce
                ]                       # Další speciální

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

        while self.cur < len(self.code):
    
            if self.code[self.cur].isalpha():         # Keywordy a identifikátory
                while self.cur < len(self.code) and self.code[self.cur].isalpha():
                    self.chars += self.code[self.cur]
                    self.cur += 1
                if self.chars.upper() in self.KEYWORDS:
                    self.tokens.append((self.chars.upper()))
                    print(self.tokens)
                else:
                    self.tokens.append(("IDENTIFIER", self.chars))
                    print(self.tokens)
        
            elif self.code[self.cur].isnumeric():
                while self.cur < len(self.code) and self.code[self.cur].isnumeric():
                    self.chars += self.code[self.cur]
                    self.cur += 1
                self.tokens.append(("NUMBER", self.chars))
                print(self.tokens)
            
            elif self.code[self.cur] == '"':        # Stringy
                self.cur += 1
                while self.cur < len(self.code) and self.code[self.cur] != '"':
                    self.chars += self.code[self.cur]
                    self.cur += 1
                self.tokens.append(("STRING", self.chars))
                print(self.tokens)
    
            elif self.code[self.cur] == ";":          # Konec statementu
                self.tokens.append(("SEMICOLON", None))
                print(self.tokens)
                self.cur += 1
            
            elif self.code[self.cur] == "/":         # Komentáře / Děleno
                if self.peek(1) == "/":
                    self.cur += 2
                    while self.cur < len(self.code) and self.code[self.cur] != "\n": self.cur += 1
                else: #NEZAPOMENOUT TO UDĚLAT I PRO /// !!!!!!
                    self.tokens.append(("SLASH", None))
                    print(self.tokens)
                    self.cur += 1
            
            elif self.code[self.cur] == "*":
                self.tokens.append(("STAR", None))
                print(self.tokens)
                self.cur += 1
    
            elif self.code[self.cur] == "=":
                self.tokens.append(("EQUAL", None))
                print(self.tokens)
                self.cur += 1
            
            elif self.code[self.cur] == "+":
                self.tokens.append(("PLUS", None))
                print(self.tokens)
                self.cur += 1
        
            elif self.code[self.cur] == "(":
                self.tokens.append(("L_PARENS", None))
                print(self.tokens)
                self.cur += 1

            elif self.code[self.cur] == ")":
                self.tokens.append(("R_PARENS", None))
                print(self.tokens)
                self.cur += 1
        
            elif self.code[self.cur] == " " or self.code[self.cur] == "\n":
                self.cur += 1

            else: # Pro mezery/ostatní znaky ignorovat zatim
                print(error(self.cur, f"Invalid Character \"{self.code[self.cur]}\""))

            self.chars = ""
    
        self.tokens.append(("EOF"))
        
        return self.tokens


# Parser (asi se zastřelim)

class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur = 0
    
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
        
        # error handling later
    
    def expression(self): # expression -> term SEMICOLON;
        return self.term()
    
        # semicolons later

    def term(self): # term -> factor ( ( "-" | "+" ) factor )* ;
        expr = self.factor()
        while self.match("PLUS", "MINUS"):
            op = self.previous()
            right = self.factor()
            expr = ("binary", expr, op, right)
        return expr

    def factor(self): # factor -> primary ( ( "/" | "*" ) primary )* ;
        expr = self.primary()
        while self.match("STAR", "SLASH"):
            op = self.previous()
            right = self.primary()
            expr = ("binary", expr, op, right)
        return expr

    def primary(self): # primary -> NUMBER | STRING | "true" | "false" | "null" | "(" expression ")" ;
        if self.match("STRING"):
            return ("string", self.previous()[1])
    
        elif self.match("NUMBER"):
            return ("number", int(self.previous()[1]))

        elif self.match("L_PARENS"):
            expr = self.expression()
            self.expect("R_PARENS", "Missing \")\" after expression.")
            return ("grouping", expr)
        
        # error handling here
    
    def parse(self):    # Hlavní funkce
        return self.expression()

# Hl. loop

if __name__ == "__main__":
    lexer = Lexer(user_code)
    lexer_out = (lexer.gettokens())
    print(lexer_out)

    parser = Parser(lexer_out)
    parser_out = parser.parse()
    print(parser_out)