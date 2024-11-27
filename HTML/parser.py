from enum import Enum, auto
from typing import Union
from .token import *
from .tokenizer import *
from .node import *


class HTMLParser:
    
    class InsertionMode(Enum):
        
        INITIAL              = auto()
        BEFORE_HTML          = auto() 
        BEFORE_HEAD          = auto() 
        IN_HEAD              = auto() 
        IN_HEAD_NOSCRIPT     = auto() 
        AFTER_HEAD           = auto() 
        IN_BODY              = auto() 
        TEXT                 = auto() 
        IN_TABLE             = auto() 
        IN_TABLE_TEXT        = auto() 
        IN_CAPTION           = auto() 
        IN_COLUMN_GROUP      = auto() 
        IN_TABLE_BODY        = auto() 
        IN_ROW               = auto() 
        IN_CELL              = auto() 
        IN_SELECT            = auto() 
        IN_SELECT_IN_TABLE   = auto() 
        IN_TEMPLATE          = auto() 
        AFTER_BODY           = auto() 
        IN_FRAMESET          = auto() 
        AFTER_FRAMESET       = auto() 
        AFTER_AFTER_BODY     = auto() 
        AFTER_AFTER_FRAMESET = auto() 
        

    whitespace  = "\t\n\f " 
    ascii_alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def __init__(self):
        
        # tokenizer
        self.tokenizer = HTMLTokenizer()
        
        # insertion modes
        self.insertion_mode = self.InsertionMode.INITIAL
        self.original_insertion_mode: self.InsertionMode = None
        
        # the output document
        self.document = HTMLNodeDocument()
        
        # stacks
        self.stack_of_open_elements: list[HTMLNodeElement] = []
        self.stack_of_template_insertion_modes = []
        self.list_of_active_formatting_elements = []
        
        # flags
        self.frameset_ok = 1
        self.scripting = 1
        self.parser_pause = 0
        self.stop = 0
        
        self.script_nesting_level = 0
        
        self.active_spectulative_html_parser = None
        
        # element pointers
        self.head_element_pointer: HTMLNodeElement = None
        self.form_element_pointer: HTMLNodeElement = None
        
        self.reprocess = 0
        
    
    def _switch_to(self, insertion_mode: "HTMLParser.InsertionMode"):
        
        self.insertion_mode = insertion_mode
        
    
    def _reprocess_token(self):
        
        self.reprocess = 1
    

    def _parse_error(self, code: str):
        
        print("Parse Error:", code)
        

    def _insert_comment_node(self, data: str, parent: HTMLNode = None):
        
        comment_node = HTMLNodeComment(data)
        parent_ = parent if parent else self.stack_of_open_elements[-1]
        parent_.children.append(comment_node)
        
        return comment_node


    def _insert_element_node_with_token(self, token: Union[HTMLTokenStartTag, HTMLTokenEndTag], parent: HTMLNode = None):
        
        element_node = HTMLNodeElement(token.tag_name, token.attributes)
        parent_ = parent if parent else self.stack_of_open_elements[-1]
        parent_.children.append(element_node)
        self.stack_of_open_elements.append(element_node)
            
        return element_node
    
    
    def _insert_element_node(self, tag_name: str, parent: HTMLNode = None):
        
        element_node = HTMLNodeElement(tag_name, [])
        parent_ = parent if parent else self.stack_of_open_elements[-1]
        parent_.children.append(element_node)
        self.stack_of_open_elements.append(element_node)
            
        return element_node
        

    def _insert_character(self, data: str, parent: HTMLNode = None):
        
        parent_ = parent if parent else self.stack_of_open_elements[-1]
        
        if len(parent_.children) > 0 and parent_.children[-1].type == HTMLNode.Type.TEXT:
            parent_.children[-1].data += data
            return None

        text_node = HTMLNodeText(data)
        parent_.children.append(text_node)
        
        return text_node
        

    def _handle_mode_initial(self, token: HTMLToken):
            
        if token.type == HTMLToken.Type.CHARACTER and token.data in self.whitespace:
            pass # ignore
        
        elif token.type == HTMLToken.Type.COMMENT:
            self._insert_comment_node(token.data, self.document)
            
        elif token.type == HTMLToken.Type.DOCTYPE:
            
            # TODO: something not implemented
            
            self.document.children.append(HTMLNodeDocumentType(token.name,\
                    token.public_identifier, token.system_identifier))
        
            self._switch_to(self.InsertionMode.BEFORE_HTML)
            
        else:
            
            # TODO: something not implemented
                
            self._switch_to(self.InsertionMode.BEFORE_HTML)
            self._reprocess_token()
            
    def _handle_mode_before_html(self, token: HTMLToken):
        
        if token.type == HTMLToken.Type.DOCTYPE:
            self._parse_error("") # ignore
        
        elif token.type == HTMLToken.Type.COMMENT:
            self._insert_comment_node(token.data, self.document)
    
        elif token.type == HTMLToken.Type.CHARACTER and token.data in self.whitespace:
            pass # ignore
        
        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "html":
            self._insert_element_node_with_token(token, self.document)
            self._switch_to(self.InsertionMode.BEFORE_HEAD)
        
        elif token.type == HTMLToken.Type.END_TAG:
            
            if token.tag_name in ("head", "body", "html", "br"):
                self._insert_element_node("html", self.document)
                self._switch_to(self.InsertionMode.BEFORE_HEAD)
                self._reprocess_token()
            
            else:
                self._parse_error("") # ignore

        else:
            self._insert_element_node("html", self.document)
            self._switch_to(self.InsertionMode.BEFORE_HEAD)
            self._reprocess_token()
    
    def _handle_mode_before_head(self, token: HTMLToken):
    
        if token.type == HTMLToken.Type.CHARACTER and token.data in self.whitespace:
            pass # ignore
        
        elif token.type == HTMLToken.Type.COMMENT:
            self._insert_comment_node(token.data)
        
        elif token.type == HTMLToken.Type.DOCTYPE:
            self._parse_error("") # ignore
            
        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "html":
            self._switch_to(self.InsertionMode.AFTER_BODY)
            self._reprocess_token()
                
        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "head":
            el = self._insert_element_node_with_token(token)
            self.head_element_pointer = el
            self._switch_to(self.InsertionMode.IN_HEAD)
        
        elif token.type == HTMLToken.Type.END_TAG:
            
            if token.tag_name in ("head", "body", "html", "br"):
                self.head_element_pointer = self._insert_element_node("head")
                self._switch_to(self.InsertionMode.IN_HEAD)
                self._reprocess_token()
        
            else:
                self._parse_error("") # ignore
            
        else:
            self.head_element_pointer = self._insert_element_node("head")
            self._switch_to(self.InsertionMode.IN_HEAD)
            self._reprocess_token()
    
    def _handle_mode_in_head(self, token: HTMLToken):
    
        if token.type == HTMLToken.Type.CHARACTER and token.data in self.whitespace:
            self._insert_character(token.data)
        
        elif token.type == HTMLToken.Type.COMMENT:
            self._insert_comment_node(token.data)
        
        elif token.type == HTMLToken.Type.DOCTYPE:
            self._parse_error("") # ignore
            
        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "html":
            self._parse_error("") 
            if any(e.type == HTMLNode.Type.ELEMENT and \
                e.tag_name == "template" for e in self.stack_of_open_elements):
                
                pass # ignore
            else:
                for attr in token.attributes:
                    if not self.stack_of_open_elements[-1].has_attr(attr[0]):
                        self.stack_of_open_elements[-1].append_attr(attr)
        
        elif token.type == HTMLToken.Type.END_TAG:
            
            if token.tag_name == "head":
                self.stack_of_open_elements.pop()
                self._switch_to(self.InsertionMode.AFTER_HEAD)
        
            elif token.tag_name in ("body", "html", "br"):
                self.stack_of_open_elements.pop()
                self._switch_to(self.InsertionMode.AFTER_HEAD)
                self._reprocess_token()
            
            else:
                self._parse_error("") # ignore 
                
        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "head":
            self._parse_error("") # ignore 
        
        else:
            self.stack_of_open_elements.pop()
            self._switch_to(self.InsertionMode.AFTER_HEAD)
            self._reprocess_token()
            
    def _handle_mode_after_head(self, token: HTMLToken):
    
        if token.type == HTMLToken.Type.CHARACTER and token.data in self.whitespace:
            self._insert_character(token.data)
        
        elif token.type == HTMLToken.Type.COMMENT:
            self._insert_comment_node(token.data)
        
        elif token.type == HTMLToken.Type.DOCTYPE:
            self._parse_error("") # ignore
            
        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "html":
            self._parse_error("") 
            if any(e.type == HTMLNode.Type.ELEMENT and \
                e.tag_name == "template" for e in self.stack_of_open_elements):
                
                pass # ignore
            else:
                for attr in token.attributes:
                    if not self.stack_of_open_elements[-1].has_attr(attr[0]):
                        self.stack_of_open_elements[-1].append_attr(attr)
            
        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "body":
            self._insert_element_node_with_token(token)
            self.frameset_ok = 0
            self._switch_to(self.InsertionMode.IN_BODY)
            
        elif token.type == HTMLToken.Type.END_TAG:
            
            if token.tag_name in ("body", "html", "br"):
                self._insert_element_node("body")
                self._switch_to(self.InsertionMode.IN_BODY)
                self._reprocess_token()

            else:                
                self._parse_error("") # ignore
                
        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "head":
            self._parse_error("") # ignore
        
        else:
            self._insert_element_node("body")
            self._switch_to(self.InsertionMode.IN_BODY)
            self._reprocess_token()
        
    def _handle_mode_in_body(self, token: HTMLToken):
        
        if token.type == HTMLToken.Type.CHARACTER and token.data == "\0":
            self._parse_error("") # ignore
        
        elif token.type == HTMLToken.Type.CHARACTER and token.data in self.whitespace:
            # TODO: reconstruct ish thing 
            self._insert_character(token.data)
            
        elif token.type == HTMLToken.Type.CHARACTER:
            # TODO: reconstruct ish thing 
            self._insert_character(token.data)
            self.frameset_ok = 0
        
        elif token.type == HTMLToken.Type.COMMENT:
            self._insert_comment_node(token.data)
        
        elif token.type == HTMLToken.Type.DOCTYPE:
            self._parse_error("") # ignore

        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "html":
            self._parse_error("") 
            if any(e.type == HTMLNode.Type.ELEMENT and \
                e.tag_name == "template" for e in self.stack_of_open_elements):
                
                pass # ignore
            else:
                for attr in token.attributes:
                    if not self.stack_of_open_elements[-1].has_attr(attr[0]):
                        self.stack_of_open_elements[-1].append_attr(attr)
                    
        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "body":
            self._parse_error("")
            assert 0, "NOT IMPLEMENTED"
            
        elif token.type == HTMLToken.Type.EOF:
            self.stop = 1
        
        elif token.type == HTMLToken.Type.END_TAG and token.tag_name == "body":
            # TODO: something not implemented
            self._switch_to(self.InsertionMode.AFTER_BODY)
        
        elif token.type == HTMLToken.Type.END_TAG and token.tag_name == "html":
            # TODO: something not implemented
            self._switch_to(self.InsertionMode.AFTER_BODY)
            self._reprocess_token()
        
        elif token.type == HTMLToken.Type.START_TAG:
            # TODO: something not implemented
            self._insert_element_node_with_token(token)
        
        elif token.type == HTMLToken.Type.END_TAG:
            pass # ignore
            
        else:
            assert 0, "UNREACHABLE"
            
    def _handle_mode_after_body(self, token: HTMLToken):
        
        if token.type == HTMLToken.Type.CHARACTER and token.data in self.whitespace:
            # TODO: reconstruct ish thing 
            self._insert_character(token.data)
        
        elif token.type == HTMLToken.Type.COMMENT:
            self._insert_comment_node(token.data, self.stack_of_open_elements[-1]) # the html element
            
        elif token.type == HTMLToken.Type.DOCTYPE:
            self._parse_error("") # ignore

        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "html":
            self._parse_error("") 
            if any(e.type == HTMLNode.Type.ELEMENT and \
                e.tag_name == "template" for e in self.stack_of_open_elements):
                
                pass # ignore
            else:
                for attr in token.attributes:
                    if not self.stack_of_open_elements[-1].has_attr(attr[0]):
                        self.stack_of_open_elements[-1].append_attr(attr)
        
        elif token.type == HTMLToken.Type.END_TAG and token.tag_name == "html":
            # TODO: something not implemented
            self._switch_to(self.InsertionMode.AFTER_AFTER_BODY)
            
        elif token.type == HTMLToken.Type.EOF:
            self.stop = 1
        
        else:
            self._parse_error("")
            self._switch_to(self.InsertionMode.IN_BODY)
            self._reprocess_token()
            
    def _handle_mode_after_after_body(self, token: HTMLToken):
        
        if token.type == HTMLToken.Type.COMMENT:
            self._insert_comment_node(token.data, self.document)
        
        elif token.type == HTMLToken.Type.CHARACTER and token.data in self.whitespace:
            # TODO: reconstruct ish thing 
            self._insert_character(token.data)
            
        elif token.type == HTMLToken.Type.DOCTYPE:
            self._parse_error("") # ignore

        elif token.type == HTMLToken.Type.START_TAG and token.tag_name == "html":
            self._parse_error("") 
            if any(e.type == HTMLNode.Type.ELEMENT and \
                e.tag_name == "template" for e in self.stack_of_open_elements):
                
                pass # ignore
            else:
                for attr in token.attributes:
                    if not self.stack_of_open_elements[-1].has_attr(attr[0]):
                        self.stack_of_open_elements[-1].append_attr(attr)
            
        elif token.type == HTMLToken.Type.EOF:
            self.stop = 1
        
        else:
            self._parse_error("")
            self._switch_to(self.InsertionMode.IN_BODY)
            self._reprocess_token()
            
    def run(self, html_text: str) -> HTMLNodeDocument:
        
        tokens = self.tokenizer.run(html_text)
        token = None
        
        # until EOF token is processed
        while not self.stop:
            
            if not self.reprocess:
                # get most recently emitted token
                token = next(tokens)
            # else: token = token # process same token
            
            # reset reprocess
            self.reprocess = 0
            
            if self.insertion_mode == self.InsertionMode.INITIAL:
                self._handle_mode_initial(token)
                
            elif self.insertion_mode == self.InsertionMode.BEFORE_HTML:
                self._handle_mode_before_html(token)
                
            elif self.insertion_mode == self.InsertionMode.BEFORE_HEAD:
                self._handle_mode_before_head(token)
                
            elif self.insertion_mode == self.InsertionMode.IN_HEAD:
                self._handle_mode_in_head(token)

            elif self.insertion_mode == self.InsertionMode.AFTER_HEAD:
                self._handle_mode_after_head(token)
                
            elif self.insertion_mode == self.InsertionMode.IN_BODY:
                self._handle_mode_in_body(token)
                
            elif self.insertion_mode == self.InsertionMode.AFTER_BODY:
                self._handle_mode_after_body(token)
                
            elif self.insertion_mode == self.InsertionMode.AFTER_AFTER_BODY:
                self._handle_mode_after_after_body(token)
            
            else:
                assert 0, "NOT IMPLEMENTED"
        
        return self.document
