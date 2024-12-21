from typing import Literal as _Literal
from decimal import Decimal as _Decimal

from .token import *


class CSSTokenizer:
        
    ascii_alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self):
        
        self.unicode_ranges_allowed = True
        
        # input to tokenize
        self.css_text: str = None
        
        # current code point (or char) index in css_text
        self.i = 0
        
        # the output
        self.tokens: list[CSSToken] = []
    
    
    def whitespace(self, c: str): return (len(c) == 1 and c in "\n\t ")
    
    
    def hex_digit(self, c: str): return (len(c) == 1 and c in "0123456789abcdefABCDEF")
    
    
    def non_ascii_ident(self, char: str):
        
        if len(char) > 1: return False
        
        code_point = ord(char)
        
        return (
            code_point == 0x00B7 or
            0x00C0 <= code_point <= 0x00D6 or
            0x00D8 <= code_point <= 0x00F6 or
            0x00F8 <= code_point <= 0x037D or
            0x037F <= code_point <= 0x1FFF or
            code_point == 0x200C or
            code_point == 0x200D or
            code_point == 0x203F or
            code_point == 0x2040 or
            0x2070 <= code_point <= 0x218F or
            0x2C00 <= code_point <= 0x2FEF or
            0x3001 <= code_point <= 0xD7FF or
            0xF900 <= code_point <= 0xFDCF or
            0xFDF0 <= code_point <= 0xFFFD or
            code_point >= 0x10000
        )
    
    
    def non_printable_code_point(self, char: str):
        
        if len(char) > 1: return False
        
        code_point = ord(char)
    
        return (
            0x0000 <= code_point <= 0x0008 or
            code_point == 0x000B or          
            0x000E <= code_point <= 0x001F or
            code_point == 0x007F             
        )
    
    
    def ident_start_code_point(self, char: str):
        
        if len(char) > 1: return False
        return self.non_ascii_ident(char) or char in self.ascii_alpha or char == "_"

    
    def ident_code_point(self, char: str):
        
        if len(char) > 1: return False
        return self.ident_start_code_point(char) or char.isdigit() or char == "-"
    
    
    def _reconsume(self):
        
        self.i -= 1
    
    
    def _consume_next_code_point(self):
        
        if self.i >= len(self.css_text):
            self.i += 1 # somehow this line fixes some errors -if it works do not touch it :D
            return "EOF"
        
        point = self.css_text[self.i]
        self.i += 1
        return point
    
    
    def _nth_next_code_point(self, n: int = 0):
        
        # NOTE: after first code point have been streamed in the run(),
        # self.i is incremented and self.css_text[self.i] becomes the next code point
        # so, if next code point is requested, n should be = 0
        # and for the second next code point n = 1 ...
        
        if self.i+n < len(self.css_text):
            return self.css_text[self.i+n]
    
        else: return "EOF"

    
    def _consume_comments(self):
        
        if self._nth_next_code_point(0) == "/" and self._nth_next_code_point(1) == "*":
            
            self.i += 2 # consume "/*"
            
            # consume until EOF or comment end
            while self.i != len(self.css_text) and not (self._nth_next_code_point(0) == "*" and self._nth_next_code_point(1) == "/"):
                self.i += 1
            
            if self.i == len(self.css_text):
                self._parse_error()
            
            else:
                self.i += 2 # consume "*/"
                
        # else not a comment: pass
        
        
    def _consume_numeric_token(self) -> CSSTokenNumber|CSSTokenPercentage|CSSTokenDimension:
        
        number = self._consume_number()
        
        if self.three_code_points_would_start_ident_sequence(n=1):
            
            token = CSSTokenDimension()
            token.value = number[0]
            token.type = number[1]
            token.sign_character = number[2]
            token.unit = ""
            
            token.unit = self._consume_ident_sequence()
            
            return token

        if self._nth_next_code_point(0) == "%":
            # consume "%"
            self.i += 1
            
            token = CSSTokenPercentage()
            token.value = number[0]
            token.sign_character = number[2]
            
            return token
        
        token = CSSTokenNumber()
        token.value = number[0]
        token.type = number[1]
        token.sign_character = number[2]
        
        return token


    def _consume_ident_like_token(self) -> CSSTokenIdent|CSSTokenFunction|CSSTokenUrl|CSSTokenBadUrl:
        
        string = self._consume_ident_sequence()
        
        if string.lower() == "url" and self._nth_next_code_point(0) == "(":
            # consume "("
            self.i += 1
            
            while self.whitespace(self._nth_next_code_point(0)) and self.whitespace(self._nth_next_code_point(1)):
                # consume next
                self.i += 1
            
            if self._nth_next_code_point(0) in "\"'" or (self.whitespace(self._nth_next_code_point(0)) and self._nth_next_code_point(1) in "\"'"):
                
                return CSSTokenFunction(string)
            
            return self._consume_url_token()
    
        if self._nth_next_code_point(0) == "(":
            # consume "("
            self.i += 1
            
            return CSSTokenFunction(string)
            
        return CSSTokenIdent(string)
        
        
    def _consume_string_token(self, ending_code_point: str = None) -> CSSTokenString|CSSTokenBadString:
        
        if ending_code_point is None:
            ending_code_point = self.css_text[self.i-1] # current code point
        
        token = CSSTokenString("")
        
        while 1:
            # consume next code point
            c = self._consume_next_code_point()
            
            if c == ending_code_point:
                return token
        
            elif c == "EOF":
                self._parse_error()
                return token
        
            elif c == "\n":
                self._parse_error()
                self._reconsume()
                return CSSTokenBadString()

            elif c == "\\":
                if self._nth_next_code_point(0) == "EOF":
                    pass # do nothing
                elif self._nth_next_code_point(0) == "\n":
                    self.i += 1 # consume "\n"
                else:
                    token.value += self._consume_escaped_code_point()
            
            else:
                token.value += c
        
    
    def _consume_url_token(self) -> CSSTokenUrl|CSSTokenBadUrl:
        
        # TODO: consider the note about the functon in reference
        token = CSSTokenUrl("")
        
        # consume as much whitespace as possible
        while self.whitespace(self._nth_next_code_point(0)):
            self.i += 1
        
        while 1:
            c = self._consume_next_code_point()
            
            if c == ")":
                return token
            
            if c == "EOF":
                self._parse_error()
                return token
            
            if self.whitespace(c):
                # consume as much whitespace as possible
                while self.whitespace(self._nth_next_code_point(0)):
                    self.i += 1
                
                if self._nth_next_code_point(0) in (")", "EOF"):
                    if self._nth_next_code_point(0) == "EOF": self._parse_error()
                    # consume it
                    self.i += 1
                    return token
                
                self._consume_remnants_of_bad_url()
                return CSSTokenBadUrl()
            
            if c in "\"'(" or self.non_printable_code_point(c):
                self._parse_error()
                self._consume_remnants_of_bad_url()
                
                return CSSTokenBadUrl()
            
            if c == "\\":
                if self.two_code_points_are_valid_escape():
                    token.value += self._consume_escaped_code_point()
                
                else:
                    self._parse_error()
                    self._consume_remnants_of_bad_url()
                
                    return CSSTokenBadUrl()
            
            else:
                token.value += c

    
    def _consume_escaped_code_point(self) -> str:
        
        # TODO: reference says something, consider it
        
        c = self._consume_next_code_point()
        
        if self.hex_digit(c):
            
            digits = c
            
            # consume as many hex digits as possible but no more than 5 (total 6)
            i = 0
            while self.hex_digit(self._nth_next_code_point(0)):
                digit = self._consume_next_code_point()
                i += 1
                digits += digit
                if i == 5:
                    break
            
            if self.whitespace(self._nth_next_code_point(0)):
                # consume it
                self.i += 1
            
            hex_value = int(digits, 16)
            if hex_value == 0 or (0xD800 <= hex_value <= 0xDFFF) or hex_value > 0x10FFFF:
                return u"\ufffd"

            return chr(hex_value)
        
        if c == "EOF":
            self._parse_error()
            return u"\ufffd"
        
        return c
    
    
    def two_code_points_are_valid_escape(self, first: str = None, second: str = None, n: int = 0):
        
        # NOTE: if n = 0 check current input stream
        # or if n = 1 check next code point ...
        
        if first is None:
            # get current and next code points
            first = self._nth_next_code_point(-1+n)
            second = self._nth_next_code_point(0+n)
            
        if first != "\\": return False
        if second == "\n": return False
        return True
    
    
    def three_code_points_would_start_ident_sequence(self, first: str = None, second: str = None, third: str = None, n: int = 0) -> bool:

        # NOTE: see note in the function above

        if first is None:
            # get current, next and third (second next) code points
            first = self._nth_next_code_point(-1+n)
            second = self._nth_next_code_point(0+n)
            third = self._nth_next_code_point(1+n)
        
        if first == "-":
            return (self.ident_start_code_point(second) or second == "-" or self.two_code_points_are_valid_escape(second, third))
        
        if self.ident_start_code_point(first): return True
        
        if first == "\\":
            return self.two_code_points_are_valid_escape(first, second)

        return False
    
    
    def three_code_points_would_start_number(self, first: str = None, second: str = None, third: str = None, n: int = 0) -> bool:

        # NOTE: see note in the function above

        if first is None:
            # get current, next and third (second next) code points
            first = self._nth_next_code_point(-1+n)
            second = self._nth_next_code_point(0+n)
            third = self._nth_next_code_point(1+n)
        
        if first in "+-":
            if second.isdigit(): return True
            
            if second == "." and third.isdigit(): return True
            
            return False
        
        if first == ".":
            return second.isdigit()
        
        if first.isdigit(): return True
        
        return False
            
    
    def three_code_points_would_start_unicode_range(self, first: str = None, second: str = None, third: str = None, n: int = 0) -> bool:
        
        # NOTE: see note in the function above

        if first is None:
            # get current, next and third (second next) code points
            first = self._nth_next_code_point(-1+n)
            second = self._nth_next_code_point(0+n)
            third = self._nth_next_code_point(1+n)
        
        return (
            first in "Uu" and 
            second == "+" and 
            (third == "?" or third in self.hex_digit(third))
        )
        

    def _consume_ident_sequence(self) -> str:
        
        # TODO: consider the note about the functon in reference
        
        result = ""
        while 1:
            
            c = self._consume_next_code_point()

            if self.ident_code_point(c):
                result += c
            
            elif self.two_code_points_are_valid_escape():
                result += self._consume_escaped_code_point()
            
            else:
                self._reconsume()
                return result
                
    
    def _consume_number(self) -> tuple[int, _Literal["integer", "number"], _Literal["+", "-"]|None]:
        
        # TODO: consider the note about the function in reference
        
        sign_character: _Literal["+", "-"]|None = None
                
        type_ = "integer"
        number_part = ""
        exponent_part = ""
        
        if self._nth_next_code_point(0) in "+-":
            # consume "+" or "-"
            c = self._consume_next_code_point()
            number_part += c
            sign_character = c
        
        while self._nth_next_code_point(0).isdigit():
            # consume it
            number_part += self._consume_next_code_point()
        
        if self._nth_next_code_point(0) == "." and self._nth_next_code_point(1).isdigit():
            # consume it
            number_part += self._consume_next_code_point()
        
            while self._nth_next_code_point(0).isdigit():
                # consume it
                number_part += self._consume_next_code_point()
        
            type_ = "number"
        
        if self._nth_next_code_point(0) in "Ee" and self._nth_next_code_point(1).isdigit():
            # consume next
            self._consume_next_code_point()
            
            while self._nth_next_code_point(0).isdigit():
                # consume it
                exponent_part += self._consume_next_code_point()
            
            type_ = "number"
            
        if self._nth_next_code_point(0) in "Ee" and self._nth_next_code_point(1) in "+-" and self._nth_next_code_point(2).isdigit():
            
            # consume next
            self._consume_next_code_point()
            # consume "+" or "-"
            exponent_part += self._consume_next_code_point()
            
            while self._nth_next_code_point(0).isdigit():
                # consume it
                exponent_part += self._consume_next_code_point()
                
            type_ = "number"
        
        value = _Decimal(number_part)
        if exponent_part != "":
            value *= _Decimal(str(pow(10, int(exponent_part))))
        value = float(value)
        return (value, type_, sign_character)
            
        
    def _consume_unicode_range_token(self) -> CSSTokenUnicodeRange:
        
        # TODO: something weird
        assert 0, "NOT IMPLEMENTED"
                
    
    def _consume_remnants_of_bad_url(self):
        
        while 1:
            c = self._consume_next_code_point()
            
            if c in (")", "EOF"):
                return
            
            if self.two_code_points_are_valid_escape():
                self._consume_escaped_code_point()
            
            # else: do nothing


    def _emit_token(self, token: CSSToken = None) -> CSSToken:
        
        if token is None:
            assert 0, "UNREACHABLE"
        
        self.tokens.append(token)
    
    
    def _parse_error(self):
        
        print("Parse error.")
        
    
    def preprocess(self, css_text: str) -> str:
        
        return css_text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n").replace("\0", u"\ufffd")
    
    
    def run(self, css_text: str) -> list[CSSToken]:
        
        self.css_text = self.preprocess(css_text)
        
        self.tokens = []
        
        self.i = 0
        while self.i <= len(self.css_text):
            
            self._consume_comments()
            
            c = self._consume_next_code_point()
            
            if self.whitespace(c):
                # consume as much whitespace as possible
                while self.whitespace(self._nth_next_code_point(0)):
                    self._consume_next_code_point()
                    
                self._emit_token(CSSTokenWhitespace())
            
            elif c == "\"":
                self._emit_token(self._consume_string_token())
            
            elif c == "#":
                if self.ident_code_point(self._nth_next_code_point(0)) or self.two_code_points_are_valid_escape(n=1):
                    
                    token = CSSTokenHash("")
                    
                    if self.three_code_points_would_start_ident_sequence(n=1):
                        token.type = "id"
                    
                    token.value += self._consume_ident_sequence()
                    
                    self._emit_token(token)
                
                else:
                    self._emit_token(CSSTokenDelim(c))
            
            elif c == "'":
                self._emit_token(self._consume_string_token())
                
            elif c == "(":
                self._emit_token(CSSTokenLeftParen())
                
            elif c == ")":
                self._emit_token(CSSTokenRightParen())
            
            elif c == "+":
                
                if self.three_code_points_would_start_number():
                    self._reconsume()
                    self._emit_token(self._consume_numeric_token())
                
                else:
                    self._emit_token(CSSTokenDelim(c))
                
            elif c == ",":
                self._emit_token(CSSTokenComma())
            
            elif c == "-":
                
                if self.three_code_points_would_start_number():
                    self._reconsume()
                    self._emit_token(self._consume_numeric_token())
                    
                elif self._nth_next_code_point(0) == "-" and self._nth_next_code_point(1) == ">":
                        # consume "->"
                        self.i += 2
                        self._emit_token(CSSTokenCDC())
                    
                elif self.three_code_points_would_start_ident_sequence():
                    self._reconsume()
                    self._emit_token(self._consume_ident_like_token())

                else:
                    self._emit_token(CSSTokenDelim(c))
            
            elif c == ".":
                
                if self.three_code_points_would_start_number():
                    self._reconsume()
                    self._emit_token(self._consume_numeric_token())
    
                else:
                    self._emit_token(CSSTokenDelim(c))
                
            elif c == ":":
                self._emit_token(CSSTokenColon())
            
            elif c == ";":
                self._emit_token(CSSTokenSemicolon())
            
            elif c == "<":
                
                if self._nth_next_code_point(0) == "!" and self._nth_next_code_point(1) == "-" and self._nth_next_code_point(2) == "-":
                    # consume "!--"
                    self.i += 3
                    self._emit_token(CSSTokenCDO())
                
                else:
                    self._emit_token(CSSTokenDelim(c))
            
            elif c == "@":
                
                if self.three_code_points_would_start_ident_sequence(n=1):
                    token = CSSTokenAtKeyword()
                    token.value = self._consume_ident_sequence()
                    self._emit_token(token)
                
                else:
                    self._emit_token(CSSTokenDelim(c))
            
            elif c == "[":
                self._emit_token(CSSTokenLeftSquare())
            
            elif c == "\\":
                
                if self.two_code_points_are_valid_escape():
                    self._reconsume()
                    self._emit_token(self._consume_ident_like_token())
                
                else:
                    self._parse_error()
                    self._emit_token(CSSTokenDelim(c))
            
            elif c == "]":
                self._emit_token(CSSTokenRightSquare())
            
            elif c == "{":
                self._emit_token(CSSTokenLeftBrace())
            
            elif c == "}":
                self._emit_token(CSSTokenRightBrace())
            
            elif c.isdigit():
                self._reconsume()
                self._emit_token(self._consume_numeric_token())
            
            elif c in "Uu":
                
                if self.unicode_ranges_allowed and self.three_code_points_would_start_unicode_range():
                    self._reconsume()
                    self._emit_token(self._consume_unicode_range_token())
                    
                self._reconsume()
                self._emit_token(self._consume_ident_like_token())
            
            elif self.ident_start_code_point(c):
                self._reconsume()
                self._emit_token(self._consume_ident_like_token())
            
            elif c == "EOF":
                self._emit_token(CSSTokenEOF())
        
            else:
                self._emit_token(CSSTokenDelim(c))

        return self.tokens
