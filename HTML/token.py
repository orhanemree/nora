from enum import Enum as _Enum, auto as _auto


__all__ = ["HTMLToken", "HTMLTokenDoctype", "HTMLTokenStartTag", "HTMLTokenEndTag", "HTMLTokenComment", "HTMLTokenCharacter", "HTMLTokenEOF", "t_HTMLToken"]


class HTMLToken:
    class Type(_Enum):

        DOCTYPE   = _auto()
        START_TAG = _auto()
        END_TAG   = _auto()
        COMMENT   = _auto()
        CHARACTER = _auto()
        EOF       = _auto()
        
        
    type: Type
    
    
    def __repr__(self):
        
        attributes = {key: getattr(self, key) for key in self.__dict__ if not key.startswith('__') and not callable(getattr(self, key))}
        attr_strings = ", ".join(f"{key}={value!r}" for key, value in attributes.items())
        
        return f"HTMLToken({attr_strings})"


class HTMLTokenDoctype(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.DOCTYPE
        
        self.name: None | str = None
        self.public_identifier: None | str = None
        self.system_identifier: None | str = None
        self.force_quirks: bool = 0
        

class HTMLTokenStartTag(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.START_TAG
        
        self.tag_name: None | str = None
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


class HTMLTokenEndTag(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.END_TAG
        
        self.tag_name: None | str = None
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
        
        
class HTMLTokenComment(HTMLToken):
    
    def __init__(self, data: str = None):
        
        self.type = self.Type.COMMENT
        
        self.data = data


class HTMLTokenCharacter(HTMLToken):
    
    def __init__(self, char: str):
        
        self.type = self.Type.CHARACTER
        
        self.data = char
        
        
class HTMLTokenEOF(HTMLToken):
    
    def __init__(self):
        
        self.type = self.Type.EOF
        

t_HTMLToken = HTMLTokenDoctype | HTMLTokenStartTag | HTMLTokenEndTag | HTMLTokenComment | HTMLTokenCharacter | HTMLTokenEOF
