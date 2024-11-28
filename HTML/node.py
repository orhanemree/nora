from enum import Enum, auto


class HTMLNode:
    
    class Type(Enum):
        
        ELEMENT                = auto()
        ATTRIBUTE              = auto()
        TEXT                   = auto()
        CDATA_SECTION          = auto()
        ENTITY_REFERENCE       = auto()
        ENTITY                 = auto()
        PROCESSING_INSTRUCTION = auto()
        COMMENT                = auto()
        DOCUMENT               = auto()
        DOCUMENT_TYPE          = auto()
        DOCUMENT_FRAGMENT      = auto()
        NOTATION               = auto()


class HTMLNodeDocument(HTMLNode):
    
    def __init__(self):
        
        self.type = self.Type.DOCUMENT
        self.children: list[HTMLNode] = []
        
        # flags
        self.parser_cannot_change_the_mode = 0
        self.is_an_iframe_srcdoc = 0
        self.quirks_mode = 0
    
    
    def __repr__(self):
        
        children = "".join(map(lambda c: str(c), self.children))
        return f"(DOCUMENT, [{children}])"


class HTMLNodeDocumentType(HTMLNode):
    
    def __init__(self, name: str, public_id: str, system_id: str):
        
        self.type = self.Type.DOCUMENT_TYPE
        self.name = name if name is not None else ""
        self.public_id = public_id if public_id is not None else ""
        self.system_id = system_id if system_id is not None else ""
        
    
    def __repr__(self):
        
        return f"(DOCUMENT_TYPE, {self.name}, {self.public_id}, {self.system_id})"
        

class HTMLNodeComment(HTMLNode):
    
    def __init__(self, data: str):
        
        self.type = self.Type.COMMENT
        self.data = data
        
    
    def __repr__(self):
        
        return f"(COMMENT, '{self.data}')"
        

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
        
    
    def __repr__(self):
        
        children = "".join(map(lambda c: str(c), self.children))
        return f"(ELEMENT, {self.tag_name}, {self.attributes}, [{children}])"
        

class HTMLNodeText(HTMLNode):
    
    def __init__(self, data: str):

        self.type = self.Type.TEXT
        self.data = data
        
    
    def __repr__(self):
        
        return f"(TEXT, '{self.data}')"
