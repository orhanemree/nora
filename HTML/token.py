from enum import Enum


class HTMLTokenType(Enum):
    
    UNKNOWN      = 0
    # tag
    OPEN_TAG     = 1 # "<"
    CLOSE_TAG    = 2 # ">"
    SLASH        = 3 # "/"
    
    # attr
    EQUALS       = 4 # "="
    SINGLE_QUOTE = 5 # "'"
    DOUBLE_QUOTE = 6 # """
    
    WHITESPACE   = 7
    STRING       = 8
    


class HTMLToken:
    
    def __init__(self, token_type: HTMLTokenType, token_value: any):
        
        self.type = token_type
        self.value = token_value
        
        
    def __iter__(self):
        
        yield self.type.name
        yield self.value
        
    
    def __repr__(self):
        
        return f"({self.type.name}, {self.value})"
