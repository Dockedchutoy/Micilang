"""
Micilang Python Interpreter

https://craftinginterpreters.com/scanning.html <- veliky dobry

TODO:
    dodělat lexer
        trochu poklidit ať je to hezky (ale nemusim)
        udelat keywaordy jaksepatri
        
    udělat parser
    ehm ehm jo
    zastrelit se (tohle je tak blby fdfsdsdg)
"""

# Získání kódu

code = "var x = 2;" \
"write(x)"      # Tady půjde Micilang kód. Soubory a shell vymyslím později.

# Queue object

class Queue():
    pass

# Error reporting

def error(position, message):
    return f"ERROR AT {position}: {message}."


# Lexer

class Lexer():
    def __init__(self): # Lexer setup

        self.KEYWORDS = ["var",          # Statementy
                "write"]        # Funkce

        self.tokens = [] # Veškeré tokeny
        self.chars = "" # momentální paměť
        self.cur = 0 # Pozice, kterou se zabývá lexer
        # code[self.cur] = CURrent position in CODE

    def advance(self):
        self.cur += 1
        self.chars = ""

    def gettokens(self):  # Pravý lexer

        while self.cur < len(code):
    
            if code[self.cur].isalpha():         # Keywordy a identifikátory
                while self.cur < len(code) and code[self.cur].isalpha():
                    self.chars += code[self.cur]
                    self.cur += 1
                if self.chars in self.KEYWORDS:
                    self.tokens.append(("KEYWORD", self.chars))
                    print(self.tokens)
                else:
                    self.tokens.append(("IDENTIFIER", self.chars))
                    print(self.tokens)
                self.chars = ""
        
            elif code[self.cur].isnumeric():
                while self.cur < len(code) and code[self.cur].isnumeric():
                    self.chars += code[self.cur]
                    self.cur += 1
                self.tokens.append(("INTEGER", self.chars))
                print(self.tokens)
                self.chars = ""
    
            elif code[self.cur] == ";":          # Konec statementu
                self.tokens.append(("ENDSTATEMENT", ";"))
                print(self.tokens)
                self.advance()
    
            elif code[self.cur] == "=":
                self.chars += code[self.cur]
                self.tokens.append(("ASSIGN", self.chars))
                print(self.tokens)
                self.advance()
        
            elif code[self.cur] == "(":
                self.tokens.append(("L_PARENS", "("))
                print(self.tokens)
                self.advance()
            elif code[self.cur] == ")":
                self.tokens.append(("R_PARENS", ")"))
                print(self.tokens)
                self.advance()
        
            elif code[self.cur] == " ":
                self.advance()
    
            else: # Pro mezery/ostatní znaky ignorovat zatim
                print(error(self.cur, f"Invalid Character \"{code[self.cur]}\""))
                self.advance()
    
        self.tokens.append(("EOF", ""))
        
        return self.tokens

lexer = Lexer()
output = (lexer.gettokens())
