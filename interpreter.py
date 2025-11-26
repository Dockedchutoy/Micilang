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

code = "var x = 2 + 1;" \
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

        self.KEYWORDS = ["VAR",          # Statementy
                "WRITE"]        # Funkce

        self.tokens = [] # Veškeré tokeny
        self.chars = "" # momentální paměť
        self.cur = 0 # Pozice, kterou se zabývá lexer
        # code[self.cur] = CURrent position in CODE

    def advance(self):
        self.cur += 1
        self.chars = ""
    
    def peek(self, n): # O kolik znaků se podívat dál?
        peeked = ""
        peek_cur = self.cur
        while self.cur < len(code) and len(peeked) < n:
            peek_cur += 1
            peeked += code[peek_cur]
        return peeked

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
                self.tokens.append(("ENDSTATEMENT"))
                print(self.tokens)
                self.advance()
            
            elif code[self.cur] == "/":
                if self.peek(1) == "/":
                    pass
    
            elif code[self.cur] == "=":
                self.tokens.append(("ASSIGN"))
                print(self.tokens)
                self.advance()
            
            elif code[self.cur] == "+":
                self.tokens.append(("PLUS"))
                print(self.tokens)
                self.advance()
        
            elif code[self.cur] == "(":
                self.tokens.append(("L_PARENS"))
                print(self.tokens)
                self.advance()

            elif code[self.cur] == ")":
                self.tokens.append(("R_PARENS"))
                print(self.tokens)
                self.advance()
        
            elif code[self.cur] == " ":
                self.advance()

            else: # Pro mezery/ostatní znaky ignorovat zatim
                print(error(self.cur, f"Invalid Character \"{code[self.cur]}\""))
                self.advance()
    
        self.tokens.append(("EOF"))
        
        return self.tokens


# Hl. loop

if __name__ == "__main__":
    lexer = Lexer()
    output = (lexer.gettokens())
    print(output)
