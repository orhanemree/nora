from enum import Enum, auto


class HTMLToken:
    
    class Type(Enum):

        DOCTYPE   = auto()
        START_TAG = auto()
        END_TAG   = auto()
        COMMENT   = auto()
        CHARACTER = auto()
        EOF       = auto()
    

class HTMLTokenDoctype(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.DOCTYPE
        self.name = ""
        self.public_identifier = ""
        self.system_identifier = ""
        self.force_quicks = 0
        
    
    def __repr__(self):
        
        return f"(DOCTYPE, {self.name}, {self.public_identifier}, {self.system_identifier}, {self.force_quicks})"
        

class HTMLTokenStartTag(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.START_TAG
        self.tag_name = ""
        self.self_closing_tag = 0
        self.attributes: list[list[str]] = [] # (name, value)
        
    
    def __repr__(self):
        
        return f"(START_TAG, {self.tag_name}, {self.self_closing_tag}, {str(self.attributes)})"
        

class HTMLTokenEndTag(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.END_TAG
        self.tag_name = ""
        self.self_closing_tag = 0
        self.attributes: list[list[str]] = [] # (name, value)
        
    
    def __repr__(self):
        
        return f"(END_TAG, {self.tag_name}, {self.self_closing_tag}, {str(self.attributes)})"
        
        
class HTMLTokenComment(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.COMMENT
        self.data = ""
        
    
    def __repr__(self):
        
        return f"(COMMENT, {self.data})"
        
        
class HTMLTokenCharacter(HTMLToken):
    
    def __init__(self, char: str):
        
        self.type = self.Type.CHARACTER
        self.data = char
        
    
    def __repr__(self):
        
        return f"(CHARACTER, {self.data})"
        
        
class HTMLTokenEOF(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.EOF
        
    
    def __repr__(self):
        
        return f"(EOF)"
