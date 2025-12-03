"""
Micilang Python Interpreter

https://craftinginterpreters.com/scanning.html <- veliky dobry

TODO:
        
    udělat parser
    ehm ehm jo
"""

# Získání kódu

user_code = 'var x = 1 * 2 + 6 / 2; // This is a comment\nprintl x;'      # Tady půjde Micilang kód. Soubory a shell vymyslím později.

user_code = "1 * 2 + (6 / 2); // 5"

# Error reporting

hadError = False

def error(position, message):
    report(position, "", message)

def report(position, item, message):
    print(f"[{position}] Error{item}: {message}")
    hadError = True


# Lexer


class Lexer():
    def __init__(self, code): # Lexer setup

        self.code = code

        self.KEYWORDS = ["VAR!", "PRINTL!", "IF!", "ELSEIF!", "ELSE!", "FUNC!", "WHILE!"         # Statementy
                "INPUT!", "NUM!"        # Funkce
                "TRUE!", "FALSE!", "NULL!"]                       # Další speciální

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
                while self.cur < len(self.code) and self.code[self.cur].isalnum():
                    self.chars += self.code[self.cur]
                    self.cur += 1
                if self.chars.upper() in self.KEYWORDS:
                    self.tokens.append((self.chars.upper(), None))
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
                self.tokens.append(("SEMICOLON", ";"))
                print(self.tokens)
                self.cur += 1
            
            elif self.code[self.cur] == "/":         # Komentáře / Děleno
                if self.peek(1) == "/":
                    self.cur += 2
                    while self.cur < len(self.code) and self.code[self.cur] != "\n": self.cur += 1
                else: #NEZAPOMENOUT TO UDĚLAT I PRO /// !!!!!!
                    self.tokens.append(("SLASH", "/"))
                    print(self.tokens)
                    self.cur += 1
            
            elif self.code[self.cur] == "*":
                self.tokens.append(("STAR", "*"))
                print(self.tokens)
                self.cur += 1
    
            elif self.code[self.cur] == "=":
                self.tokens.append(("EQUAL", "="))
                print(self.tokens)
                self.cur += 1
            
            elif self.code[self.cur] == "+":
                self.tokens.append(("PLUS", "+"))
                print(self.tokens)
                self.cur += 1
        
            elif self.code[self.cur] == "(":
                self.tokens.append(("L_PARENS", "("))
                print(self.tokens)
                self.cur += 1

            elif self.code[self.cur] == ")":
                self.tokens.append(("R_PARENS", ")"))
                print(self.tokens)
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

class Literal(Expr):
    def __init__(self, val):
        self.val = val
    
    def __str__(self):
        return f"{self.val}"

    def accept(self, visitor):
        return visitor.visitLiteral(self)

class Group(Expr):
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return f"Group({self.expression})"

    def accept(self, visitor):
        return visitor.visitGroup(self)

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"Binary({self.left}, {self.operator}, {self.right})"
    
    def accept(self, visitor):
        return visitor.visitBinary(self)


# Parser (asi se zastřelim)


class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur = 0
    
    def error(self, token, message):
        error(token, message)
    
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
    
    def expression(self): # expression -> term SEMICOLON;
        return self.term()
    
        # semicolons later for statements

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

    def primary(self): # primary -> NUMBER | STRING | "true" | "false" | "null" | "(" expression ")" ;
        if self.match("NUMBER") or self.match("STRING"):
            return Literal(int(self.previous()[1]))

        elif self.match("L_PARENS"):
            expr = self.expression()
            self.expect("R_PARENS", "Missing \")\" after expression.")
            return Group(expr)
        
        self.error(self.peek(), "Missing expression")
    
    def parse(self):    # Hlavní funkce
        return self.expression()


# Interpreter


class Interpreter():
    def __init__(self):
        pass

    def evaluate(self, expr):       # Přesune nás zase na interpretu visitor
        return expr.accept(self)

    def visitLiteral(self, expr):   # Čísla, řetězce, booleany
        return expr.val

    def visitGroup(self, expr):     # ( )
        return self.evaluate(expr.expression)

    def visitBinary(self, expr):       # Binární operace
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator:
            case "PLUS":
                if isinstance(left, float) and isinstance(right, float):  # Sčítání čísel
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
    
    def interpret(self, expression):
        value = self.evaluate(expression)
        print(value)



# Hl. loop


if __name__ == "__main__":

    lexer = Lexer(user_code)
    lexer_out = (lexer.gettokens())
    print(lexer_out)

    parser = Parser(lexer_out)
    parser_out = parser.parse()
    print(parser_out)

    interpreter = Interpreter()
    interpreter.interpret(parser_out)