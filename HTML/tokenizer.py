from enum import Enum, auto
from .token import *


class HTMLTokenizer:

    class State(Enum):
    
        DATA                                          = auto()
        TAG_OPEN                                      = auto()
        END_TAG_OPEN                                  = auto()
        TAG_NAME                                      = auto()
        BEFORE_ATTRIBUTE_NAME                         = auto()
        ATTRIBUTE_NAME                                = auto()
        AFTER_ATTRIBUTE_NAME                          = auto()
        BEFORE_ATTRIBUTE_VALUE                        = auto()
        ATTRIBUTE_VALUE_DOUBLE_QUOTED                 = auto()
        ATTRIBUTE_VALUE_SINGLE_QUOTED                 = auto()
        ATTRIBUTE_VALUE_UNQUOTED                      = auto()
        AFTER_ATTRIBUTE_VALUE_QUOTED                  = auto()
        SELF_CLOSING_START_TAG                        = auto()
        MARKUP_DECLARATION_OPEN                       = auto()
        COMMENT_START                                 = auto()
        COMMENT_START_DASH                            = auto()
        COMMENT                                       = auto()
        COMMENT_LESS_THAN_SIGN                        = auto() 
        COMMENT_LESS_THAN_SIGN_BANG                   = auto() 
        COMMENT_LESS_THAN_SIGN_BANG_DASH              = auto() 
        COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH         = auto() 
        COMMENT_END_DASH                              = auto()
        COMMENT_END                                   = auto()
        COMMENT_END_BANG                              = auto()
        DOCTYPE                                       = auto()
        BEFORE_DOCTYPE_NAME                           = auto()
        DOCTYPE_NAME                                  = auto()
        AFTER_DOCTYPE_NAME                            = auto()
        AFTER_DOCTYPE_PUBLIC_KEYWORD                  = auto()
        BEFORE_DOCTYPE_PUBLIC_IDENTIFIER              = auto()
        DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED       = auto()
        DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED       = auto()
        AFTER_DOCTYPE_PUBLIC_IDENTIFIER               = auto()
        BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS = auto()
        AFTER_DOCTYPE_SYSTEM_KEYWORD                  = auto()
        BEFORE_DOCTYPE_SYSTEM_IDENTIFIER              = auto()
        DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED       = auto()
        DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED       = auto()
        AFTER_DOCTYPE_SYSTEM_IDENTIFIER               = auto()
        
    
    whitespace  = "\t\n\f " 
    ascii_alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def __init__(self):
        
        self.parser_pause = 0
        self.state = self.State.DATA
        self.curr_token: HTMLToken = None
        self.output_tokens: list[HTMLToken] = []
        self.i = 0
        
    
    def _switch_to(self, state: "HTMLTokenizer.State", reconsume: int = 0):
        
        self.state = state
        
        if reconsume:
            self.i -= 1
    
    
    def _emit_curr_token(self):
        
        self.output_tokens.append(self.curr_token)
        self.curr_token = None
    

    def run(self, html_text: str):
        
        html_text = html_text.strip()
        
        while not self.parser_pause and self.i < len(html_text):
            
            c = html_text[self.i]
            
            if self.state == self.State.DATA:
                
                if c == "&":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == "<":
                    self._switch_to(self.State.TAG_OPEN)
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    self.curr_token = HTMLTokenCharacter(c)
                    self._emit_curr_token()
            
            elif self.state == self.State.TAG_OPEN:
                
                if c == "!":
                    self._switch_to(self.State.MARKUP_DECLARATION_OPEN)
                    
                elif c == "/":
                    self._switch_to(self.State.END_TAG_OPEN)
                    
                elif c in self.ascii_alpha:
                    self.curr_token = HTMLTokenStartTag()
                    self._switch_to(self.State.TAG_NAME, 1)
                    # reconsume

                elif c == "?":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    assert 0, "NOT IMPLEMENTED"
                    
            elif self.state == self.State.END_TAG_OPEN:
                
                if c in self.ascii_alpha:
                    self.curr_token = HTMLTokenEndTag()
                    self._switch_to(self.State.TAG_NAME, 1)
                    # reconsume
                    
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.TAG_NAME:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                    
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    self.curr_token.tag_name += c.lower()
            
            elif self.state == self.State.BEFORE_ATTRIBUTE_NAME:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c in "/>":
                    self._switch_to(self.State.AFTER_ATTRIBUTE_NAME, 1)
                    # reconsume
                
                elif c == "=":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self.curr_token.attributes.append(["", "" ])
                    self._switch_to(self.State.ATTRIBUTE_NAME, 1)
                    # reconsume
            
            elif self.state == self.State.ATTRIBUTE_NAME:
                
                if c in self.whitespace or c in "/>":
                    self._switch_to(self.State.AFTER_ATTRIBUTE_NAME, 1)
                    # reconsume
                
                elif c == "=":
                    self._switch_to(self.State.BEFORE_ATTRIBUTE_VALUE)
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c in "\"'<":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    self.curr_token.attributes[-1][0] += c.lower()
                
                # TODO: check if same attr name exists already in the token see
                # https://html.spec.whatwg.org/multipage/parsing.html#attribute-name-state
            
            elif self.state == self.State.AFTER_ATTRIBUTE_NAME:

                if c in self.whitespace:
                    pass # ignore
                    
                elif c == "/":
                    self._switch_to(self.State.SELF_CLOSING_START_TAG)
                
                elif c == "=":
                    self._switch_to(self.State.BEFORE_ATTRIBUTE_VALUE)
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()
                
                else:
                    self.curr_token.attributes.append(["", "" ])
                    self._switch_to(self.State.ATTRIBUTE_NAME, 1)
                    # reconsume
                    
            elif self.state == self.State.BEFORE_ATTRIBUTE_VALUE:
                
                if c in self.whitespace:
                    pass # ignore 
                
                elif c == "\"":
                    self._switch_to(self.State.ATTRIBUTE_VALUE_DOUBLE_QUOTED)
                
                elif c == "'":
                    self._switch_to(self.State.ATTRIBUTE_VALUE_SINGLE_QUOTED)
                
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self._switch_to(self.State.ATTRIBUTE_VALUE_UNQUOTED, 1)
                    # reconsume

            elif self.state == self.State.ATTRIBUTE_VALUE_DOUBLE_QUOTED:
                
                if c == "\"":
                    self._switch_to(self.State.AFTER_ATTRIBUTE_VALUE_QUOTED)
                    
                elif c == "&":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self.curr_token.attributes[-1][1] += c
            
            elif self.state == self.State.ATTRIBUTE_VALUE_SINGLE_QUOTED:
                
                if c == "'":
                    self._switch_to(self.State.AFTER_ATTRIBUTE_VALUE_QUOTED)
                    
                elif c == "&":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self.curr_token.attributes[-1][1] += c
            
            elif self.state == self.State.ATTRIBUTE_VALUE_UNQUOTED:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                    
                elif c == "&":
                    assert 0, "NOT IMPLEMENTED"

                elif c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()

                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                    
                elif c in "\"'<=`":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    self.curr_token.attributes[-1][1] += c
            
            elif self.state == self.State.AFTER_ATTRIBUTE_VALUE_QUOTED:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                    
                elif c == "/":
                    self._switch_to(self.State.SELF_CLOSING_START_TAG)
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()
                
                else:
                    assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.SELF_CLOSING_START_TAG:
                
                if c == ">":
                    self.curr_token.self_closing_tag = 1
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()
                
                else:
                    assert 0, "NOT IMPLEMENETED"
                    
            elif self.state == self.State.MARKUP_DECLARATION_OPEN:
                
                if self.i+1 < len(html_text) and html_text[self.i:self.i+2] == "--":
                    self.curr_token = HTMLTokenComment()
                    self._switch_to(self.State.COMMENT_START)
                    self.i += 1 # consume the second "-"
                
                elif self.i+6 < len(html_text) and html_text[self.i:self.i+7].upper() == "DOCTYPE":
                    self._switch_to(self.State.DOCTYPE)
                    self.i += 6 # consume the rest "OCTYPE" 
                
                else:
                    assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.COMMENT_START:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_START_DASH)
                
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self._switch_to(self.State.COMMENT, 1)
                    # reconsume
                    
            elif self.state == self.State.COMMENT_START_DASH:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_END)
                
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self.curr_token.data += "-"
                    self._switch_to(self.State.COMMENT, 1)
                    # reconsume
                    
            elif self.state == self.State.COMMENT:
                
                if c == "<":
                    self.curr_token.data += c
                    self._switch_to(self.State.COMMENT_LESS_THAN_SIGN)
                
                elif c == "-":
                    self._switch_to(self.State.COMMENT_END_DASH)
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self.curr_token.data += c
            
            elif self.state == self.State.COMMENT_LESS_THAN_SIGN:
                
                if c == "!":
                    self.curr_token.data += c
                    self._switch_to(self.State.COMMENT_LESS_THAN_SIGN_BANG)
                
                elif c == "<":
                    self.curr_token.data += c 
                
                else:
                    self._switch_to(self.State.COMMENT, 1)
                    # reconsume
            
            elif self.state == self.State.COMMENT_LESS_THAN_SIGN_BANG:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_LESS_THAN_SIGN_BANG_DASH)
                
                else:
                    self._switch_to(self.State.COMMENT, 1)
                    # reconsume    
                    
            elif self.state == self.State.COMMENT_LESS_THAN_SIGN_BANG_DASH:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH)
                
                else:
                    self._switch_to(self.State.COMMENT_END_DASH, 1)
                    # reconsume    
                    
            elif self.state == self.State.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH:
                
                if c == ">":
                    self._switch_to(self.State.COMMENT_END, 1)
                    # reconsume
                
                else:
                    assert 0, "NOT IMPLEMENETED"
                    
            elif self.state == self.State.COMMENT_END_DASH:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_END)
                
                else:
                    self.curr_token.data += "-"
                    self._switch_to(self.State.COMMENT, 1)
                    # reconsume
                    
            elif self.state == self.State.COMMENT_END:
                
                if c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()

                elif c == "!":
                    self._switch_to(self.State.COMMENT_END_BANG)
                
                elif c == "-":
                    self.curr_token.data += c
                    
                else:
                    self.curr_token.data += "--"
                    self._switch_to(self.State.COMMENT, 1)
                    # reconsume
                    
            elif self.state == self.State.COMMENT_END_BANG:
                
                if c == "-":
                    self.curr_token.data += "--!"
                    self._switch_to(self.State.COMMENT_END_DASH)
                
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    self.curr_token.data += "--!"
                    self._switch_to(self.State.COMMENT, 1)
                    # reconsume
            
            elif self.state == self.State.DOCTYPE:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_DOCTYPE_NAME)
                
                elif c == ">":
                    self._switch_to(self.State.BEFORE_DOCTYPE_NAME, 1)
                    # reconsume
                
                else:
                    assert 0, "NOT IMPLEMENTED"
                    
            elif self.state == self.State.BEFORE_DOCTYPE_NAME:
                
                if c in self.whitespace:
                    pass # ignore
                    
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                    
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self.curr_token = HTMLTokenDoctype()
                    self.curr_token.name = c.lower()
                    self._switch_to(self.State.DOCTYPE_NAME)
            
            elif self.state == self.State.DOCTYPE_NAME:
            
                if c in self.whitespace:
                    self._switch_to(self.State.AFTER_DOCTYPE_NAME)
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self.curr_token.name += c.lower()
            
            elif self.state == self.State.AFTER_DOCTYPE_NAME:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()
                
                else:
                
                    if self.i+5 < len(html_text) and html_text[self.i:self.i+6].upper() == "PUBLIC":
                        self._switch_to(self.State.AFTER_DOCTYPE_PUBLIC_KEYWORD)
                        self.i += 5 # consume the rest "UBLIC"
                    
                    elif self.i+5 < len(html_text) and html_text[self.i:self.i+6].upper() == "SYSTEM":
                        self._switch_to(self.State.AFTER_DOCTYPE_SYSTEM_KEYWORD)
                        self.i += 5 # consume the rest "YSTEM"
                    
                    else:
                        assert 0, "NOT IMPLEMENTED"
                        
            elif self.state == self.State.AFTER_DOCTYPE_PUBLIC_KEYWORD:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER)
                
                elif c == "\"":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == "'":
                    assert 0, "NOT IMPLEMENTED"
                    
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c == "\"":
                    self._switch_to(self.State.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED)
                
                elif c == "'":
                    self._switch_to(self.State.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED)
                    
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    assert 0, "NOT IMPLEMENTED"
                
            elif self.state == self.State.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED:
                
                if c == "\"":
                    self._switch_to(self.State.AFTER_DOCTYPE_PUBLIC_IDENTIFIER)
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    self.curr_token.public_identifier += c
                    
            elif self.state == self.State.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED:
                
                if c == "'":
                    self._switch_to(self.State.AFTER_DOCTYPE_PUBLIC_IDENTIFIER)
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    self.curr_token.public_identifier += c
            
            elif self.state == self.State.AFTER_DOCTYPE_PUBLIC_IDENTIFIER:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS)
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()
                
                elif c == "\"":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == "'":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    assert 0, "NOT IMPLEMENTED"
                    
            elif self.state == self.State.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()
                
                elif c == "\"":
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED)
                
                elif c == "'":
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED)
                
                else:
                    assert 0, "NOT IMPLEMENTED"
                    
            elif self.state == self.State.AFTER_DOCTYPE_SYSTEM_KEYWORD:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER)
                
                elif c == "\"":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == "'":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    assert 0, "NOT IMPLEMENTED"
                    
            elif self.state == self.State.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c == "\"":
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED)
                
                elif c == "'":
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED)
                
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                
                else:
                    assert 0, "NOT IMPLEMENTED"
                    
            elif self.state == self.State.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED:
                
                if c == "\"":
                    self._switch_to(self.State.AFTER_DOCTYPE_SYSTEM_IDENTIFIER)
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self.curr_token.system_identifier += c
                    
            elif self.state == self.State.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED:
                
                if c == "'":
                    self._switch_to(self.State.AFTER_DOCTYPE_SYSTEM_IDENTIFIER)
                
                elif c == "\0":
                    assert 0, "NOT IMPLEMENTED"
                
                elif c == ">":
                    assert 0, "NOT IMPLEMENTED"
                    
                else:
                    self.curr_token.system_identifier += c
                    
            elif self.state == self.State.AFTER_DOCTYPE_SYSTEM_IDENTIFIER:
                
                if c in self.whitespace:
                    pass # ignore
                    
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    self._emit_curr_token()
                
                else:
                    assert 0, "NOT IMPLEMENTED"
            
            self.i += 1 # consume char
        
        # add EOF token
        self.curr_token = HTMLTokenEOF()
        self._emit_curr_token()

        return self.output_tokens
    