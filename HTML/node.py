from enum import Enum as _Enum, auto as _auto


__all__ = ["HTMLNode", "HTMLNodeDocument", "HTMLNodeDocumentType", "HTMLNodeComment", "HTMLNodeElement", "HTMLNodeText", "t_HTMLNode"]


class HTMLNode:
    
    class Type(_Enum):
        
        ELEMENT                = _auto()
        ATTRIBUTE              = _auto()
        TEXT                   = _auto()
        CDATA_SECTION          = _auto()
        ENTITY_REFERENCE       = _auto()
        ENTITY                 = _auto()
        PROCESSING_INSTRUCTION = _auto()
        COMMENT                = _auto()
        DOCUMENT               = _auto()
        DOCUMENT_TYPE          = _auto()
        DOCUMENT_FRAGMENT      = _auto()
        NOTATION               = _auto()

        
    type: Type
    
    
    def __repr__(self):
        
        attributes = {key: getattr(self, key) for key in self.__dict__ if not key.startswith('__') and not callable(getattr(self, key))}
        attr_strings = ", ".join(f"{key}={value!r}" for key, value in attributes.items())
        
        return f"HTMLNode({attr_strings})"
    

class HTMLNodeDocument(HTMLNode):
    
    def __init__(self):
        
        self.type = self.Type.DOCUMENT
        self.children: list[HTMLNode] = []
        
        # flags
        self.parser_cannot_change_the_mode: bool = 0
        self.is_an_iframe_srcdoc: bool = 0
        self.quirks_mode: bool = 0
    
    
class HTMLNodeDocumentType(HTMLNode):
    
    def __init__(self, name: None|str, public_id: None|str, system_id: None|str):
        
        self.type = self.Type.DOCUMENT_TYPE
        
        self.name = name if name is not None else ""
        self.public_id = public_id if public_id is not None else ""
        self.system_id = system_id if system_id is not None else ""
        
    
class HTMLNodeComment(HTMLNode):
    
    def __init__(self, data: str):
        
        self.type = self.Type.COMMENT
        
        self.data = data
        
    
class HTMLNodeElement(HTMLNode):
    
    def __init__(self, tag_name: str, attributes: list[dict[str, str]]):
        
        self.type = self.Type.ELEMENT
        
        self.tag_name = tag_name
        self.attributes = attributes
        self.children: list[HTMLNode] = []
    
    
    def append_attr(self, name: str, value: str):
        
        self.attributes.append([name, value])
       
        
    def has_attr(self, name: str):
        
        return any(a[0] == name for a in self.attributes)
    
    
    def get_attr(self, name: str):
        
        if not self.has_attr(name):
            return
        
        return list(filter(lambda a: a[0] == name, self.attributes))[0][1]
        
    
class HTMLNodeText(HTMLNode):
    
    def __init__(self, data: str):

        self.type = self.Type.TEXT
        
        self.data = data
        
    
t_HTMLNode = HTMLNodeDocument | HTMLNodeDocumentType | HTMLNodeComment | HTMLNodeElement | HTMLNodeText
