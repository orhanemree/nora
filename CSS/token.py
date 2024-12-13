from enum import Enum as _Enum, auto as _auto
from typing import Literal as _Literal


class CSSToken:
    
    class Type(_Enum):
        
        IDENT         = _auto()
        FUNCTION      = _auto()
        AT_KEYWORD    = _auto()
        HASH          = _auto()
        STRING        = _auto()
        BAD_STRING    = _auto()
        URL           = _auto()
        BAD_URL       = _auto()
        DELIM         = _auto()
        NUMBER        = _auto()
        PERCENTAGE    = _auto()
        DIMENSION     = _auto()
        UNICODE_RANGE = _auto()
        WHITESPACE    = _auto()
        CDO           = _auto()
        CDC           = _auto()
        COLON         = _auto()
        SEMICOLON     = _auto()
        COMMA         = _auto()
        LEFT_SQUARE   = _auto()
        RIGHT_SQUARE  = _auto()
        LEFT_PAREN    = _auto()
        RIGHT_PAREN   = _auto()
        LEFT_BRACE    = _auto()
        RIGHT_BRACE   = _auto()
    
    
    type: Type
    
    
    def __repr__(self):
        
        attributes = {key: getattr(self, key) for key in self.__dict__ if not key.startswith('__') and not callable(getattr(self, key))}
        attr_strings = ", ".join(f"{key}={value!r}" for key, value in attributes.items())
        
        return f"CSSToken({attr_strings})"


class CSSTokenIdent(CSSToken):
    
    def __init__(self, value: str = None):
        
        self.tok_type = self.Type.IDENT
        
        self.value = value


class CSSTokenFunction(CSSToken):
    
    def __init__(self, value: str = None):
        
        self.tok_type = self.Type.FUNCTION
        
        self.value = value


class CSSTokenAtKeyword(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.AT_KEYWORD
        
        self.value: None|str = None


class CSSTokenHash(CSSToken):
    
    def __init__(self, value: str = None):
        
        self.tok_type = self.Type.HASH
        
        self.value = value
        self.type: _Literal["id", "unrestricted"] = "unrestricted"


class CSSTokenString(CSSToken):
    
    def __init__(self, value: None|str = None):
        
        self.tok_type = self.Type.STRING
        
        self.value = value


class CSSTokenBadString(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.BAD_STRING
        
        self.value: None|str = None


class CSSTokenUrl(CSSToken):
    
    def __init__(self, value: str = None):
        
        self.tok_type = self.Type.URL
        
        self.value = value


class CSSTokenBadUrl(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.BAD_URL
        
        self.value: None|str = None


class CSSTokenDelim(CSSToken):
    
    def __init__(self, value: None|str = None):
        
        self.tok_type = self.Type.DELIM
        
        self.value = value


class CSSTokenNumber(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.NUMBER
        
        self.value: None|int|float = None
        self.type: _Literal["integer", "number"] = "integer"
        self.sign_character: _Literal["+", "-"]|None = None


class CSSTokenPercentage(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.PERCENTAGE
        
        self.value: None|int|float = None
        self.sign_character: _Literal["+", "-"]|None = None


class CSSTokenDimension(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.DIMENSION
        
        self.value: None|int|float = None
        self.type: _Literal["integer", "number"] = "integer"
        self.sign_character: _Literal["+", "-"]|None = None
        self.unit: None|str = None


class CSSTokenUnicodeRange(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.UNICODE_RANGE
        
        self.starting: None|str = None
        self.ending: None|str = None


class CSSTokenWhitespace(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.WHITESPACE


class CSSTokenCDO(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.CDO


class CSSTokenCDC(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.CDC


class CSSTokenColon(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.COLON


class CSSTokenSemicolon(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.SEMICOLON


class CSSTokenComma(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.COMMA


class CSSTokenLeftSquare(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.LEFT_SQUARE
        

class CSSTokenRightSquare(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.RIGHT_SQUARE


class CSSTokenLeftParen(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.LEFT_PAREN


class CSSTokenRightParen(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.RIGHT_PAREN


class CSSTokenLeftBrace(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.LEFT_BRACE


class CSSTokenRightBrace(CSSToken):
    
    def __init__(self):
        
        self.tok_type = self.Type.RIGHT_BRACE
        