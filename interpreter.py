"""
Micilang Python Interpreter

https://craftinginterpreters.com/scanning.html <- veliky dobry

TODO:
    dodělat lexer
        trochu poklidit ať je to hezky (ale nemusim)
        udelat keywaordy jaksepatri
        
    udělat parser
    ehm ehm jo
"""

# Získání kódu

user_code = "var x = 2 + 1; // This is a comment\nwrite(x);"      # Tady půjde Micilang kód. Soubory a shell vymyslím později.

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
                self.chars = ""
        
            elif self.code[self.cur].isnumeric():
                while self.cur < len(self.code) and self.code[self.cur].isnumeric():
                    self.chars += self.code[self.cur]
                    self.cur += 1
                self.tokens.append(("INTEGER", self.chars))
                print(self.tokens)
                self.chars = ""
    
            elif self.code[self.cur] == ";":          # Konec statementu
                self.tokens.append(("ENDSTATEMENT"))
                print(self.tokens)
                self.advance()
            
            elif self.code[self.cur] == "/":         # Komentáře / Děleno
                if self.peek(1) == "/":
                    self.cur += 2
                    while self.cur < len(self.code) and self.code[self.cur] != "\n": self.cur += 1
                else: #NEZAPOMENOUT TO UDĚLAT I PRO /// !!!!!!
                    self.tokens.append(("DIVIDE"))
                    print(self.tokens)
                    self.advance()
    
            elif self.code[self.cur] == "=":
                self.tokens.append(("ASSIGN"))
                print(self.tokens)
                self.advance()
            
            elif self.code[self.cur] == "+":
                self.tokens.append(("PLUS"))
                print(self.tokens)
                self.advance()
        
            elif self.code[self.cur] == "(":
                self.tokens.append(("L_PARENS"))
                print(self.tokens)
                self.advance()

            elif self.code[self.cur] == ")":
                self.tokens.append(("R_PARENS"))
                print(self.tokens)
                self.advance()
        
            elif self.code[self.cur] == " " or self.code[self.cur] == "\n":
                self.advance()

            else: # Pro mezery/ostatní znaky ignorovat zatim
                print(error(self.cur, f"Invalid Character \"{self.code[self.cur]}\""))
                self.advance()
    
        self.tokens.append(("EOF"))
        
        return self.tokens


# Parser (asi se zastřelim)

class Parser():
    def __init__(self):
        pass

# Hl. loop

if __name__ == "__main__":
    lexer = Lexer(user_code)
    output = (lexer.gettokens())
    print(output)
