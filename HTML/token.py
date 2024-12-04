from enum import Enum, auto
from typing import Union


class HTMLToken:
    
    class Type(Enum):

        DOCTYPE   = auto()
        START_TAG = auto()
        END_TAG   = auto()
        COMMENT   = auto()
        CHARACTER = auto()
        EOF       = auto()
    
    
    type: Type


class HTMLTokenDoctype(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.DOCTYPE
        
        self.name: Union[str, None] = None
        self.public_identifier: Union[str, None] = None
        self.system_identifier: Union[str, None] = None
        self.force_quirks: bool = 0
        
    
    def __repr__(self):
        
        return f"(DOCTYPE, {self.name}, {self.public_identifier}, {self.system_identifier}, {self.force_quirks})"
        

class HTMLTokenStartTag(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.START_TAG
        
        self.tag_name: Union[str, None] = None
        self.self_closing_tag: bool = 0
        self.attributes: list[list[str, str]] = [] # (name, value)
    
    
    def append_attr(self, name: str, value: str):
        
        self.attributes.append([name, value])
       
        
    def has_attr(self, name: str):
        
        return any(a[0] == name for a in self.attributes)
    
    
    def get_attr(self, name: str):
        
        if not self.has_attr(name):
            return
        
        return list(filter(lambda a: a[0] == name, self.attributes))[0][1]

    
    def __repr__(self):
        
        return f"(START_TAG, {self.tag_name}, {self.self_closing_tag}, {str(self.attributes)})"
        

class HTMLTokenEndTag(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.END_TAG
        
        self.tag_name: Union[str, None] = None
        self.self_closing_tag: bool = 0
        self.attributes: list[list[str, str]] = [] # (name, value)
    
    
    def append_attr(self, name: str, value: str):
        
        self.attributes.append([name, value])
       
        
    def has_attr(self, name: str):
        
        return any(a[0] == name for a in self.attributes)
    
    
    def get_attr(self, name: str):
        
        if not self.has_attr(name):
            return
        
        return list(filter(lambda a: a[0] == name, self.attributes))[0][1]
        
    
    def __repr__(self):
        
        return f"(END_TAG, {self.tag_name}, {self.self_closing_tag}, {str(self.attributes)})"
        
        
class HTMLTokenComment(HTMLToken):
    
    def __init__(self, data: str = None):
        
        self.type = self.Type.COMMENT
        
        self.data = data
        
    
    def __repr__(self):
        
        return f"(COMMENT, '{self.data}')"
        
        
class HTMLTokenCharacter(HTMLToken):
    
    def __init__(self, char: str):
        
        self.type = self.Type.CHARACTER
        
        self.data = char
        
    
    def __repr__(self):
        
        return f"(CHARACTER, '{self.data}')"
        
        
class HTMLTokenEOF(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.EOF
        
    
    def __repr__(self):
        
        return f"(EOF)"


t_HTMLToken = Union[HTMLTokenDoctype, HTMLTokenStartTag, HTMLTokenEndTag, HTMLTokenComment, HTMLTokenCharacter, HTMLTokenEOF]
