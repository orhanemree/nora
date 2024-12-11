from enum import Enum as _Enum, auto as _auto
from typing import Generator as _Generator

from .token import *


__all__ = ["HTMLTokenizer"]


class HTMLTokenizer:

    class State(_Enum):
    
        DATA                                          = _auto()
        RCDATA                                        = _auto()
        RAWTEXT                                       = _auto()
        SCRIPT_DATA                                   = _auto()
        PLAIN_TEXT                                    = _auto()
        TAG_OPEN                                      = _auto()
        END_TAG_OPEN                                  = _auto()
        TAG_NAME                                      = _auto()
        RCDATA_LESS_THAN_SIGN                         = _auto()
        RCDATA_END_TAG_OPEN                           = _auto()
        RCDATA_END_TAG_NAME                           = _auto()
        RAWTEXT_LESS_THAN_SIGN                        = _auto()
        RAWTEXT_END_TAG_OPEN                          = _auto()
        RAWTEXT_END_TAG_NAME                          = _auto()
        SCRIPT_DATA_LESS_THAN_SIGN                    = _auto()
        SCRIPT_DATA_END_TAG_OPEN                      = _auto()
        SCRIPT_DATA_END_TAG_NAME                      = _auto()
        SCRIPT_DATA_ESCAPE_START                      = _auto()
        SCRIPT_DATA_ESCAPE_START_DASH                 = _auto()
        SCRIPT_DATA_ESCAPED                           = _auto()
        SCRIPT_DATA_ESCAPED_DASH                      = _auto()
        SCRIPT_DATA_ESCAPED_DASH_DASH                 = _auto()
        SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN            = _auto()
        SCRIPT_DATA_ESCAPED_END_TAG_OPEN              = _auto()
        SCRIPT_DATA_ESCAPED_END_TAG_NAME              = _auto()
        SCRIPT_DATA_DOUBLE_ESCAPE_START               = _auto()
        SCRIPT_DATA_DOUBLE_ESCAPED                    = _auto()
        SCRIPT_DATA_DOUBLE_ESCAPED_DASH               = _auto()
        SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH          = _auto()
        SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN     = _auto()
        SCRIPT_DATA_DOUBLE_ESCAPE_END                 = _auto()
        BEFORE_ATTRIBUTE_NAME                         = _auto()
        ATTRIBUTE_NAME                                = _auto()
        AFTER_ATTRIBUTE_NAME                          = _auto()
        BEFORE_ATTRIBUTE_VALUE                        = _auto()
        ATTRIBUTE_VALUE_DOUBLE_QUOTED                 = _auto()
        ATTRIBUTE_VALUE_SINGLE_QUOTED                 = _auto()
        ATTRIBUTE_VALUE_UNQUOTED                      = _auto()
        AFTER_ATTRIBUTE_VALUE_QUOTED                  = _auto()
        SELF_CLOSING_START_TAG                        = _auto()
        BOGUS_COMMENT                                 = _auto()
        MARKUP_DECLARATION_OPEN                       = _auto()
        COMMENT_START                                 = _auto()
        COMMENT_START_DASH                            = _auto()
        COMMENT                                       = _auto()
        COMMENT_LESS_THAN_SIGN                        = _auto() 
        COMMENT_LESS_THAN_SIGN_BANG                   = _auto() 
        COMMENT_LESS_THAN_SIGN_BANG_DASH              = _auto() 
        COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH         = _auto() 
        COMMENT_END_DASH                              = _auto()
        COMMENT_END                                   = _auto()
        COMMENT_END_BANG                              = _auto()
        DOCTYPE                                       = _auto()
        BEFORE_DOCTYPE_NAME                           = _auto()
        DOCTYPE_NAME                                  = _auto()
        AFTER_DOCTYPE_NAME                            = _auto()
        AFTER_DOCTYPE_PUBLIC_KEYWORD                  = _auto()
        BEFORE_DOCTYPE_PUBLIC_IDENTIFIER              = _auto()
        DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED       = _auto()
        DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED       = _auto()
        AFTER_DOCTYPE_PUBLIC_IDENTIFIER               = _auto()
        BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS = _auto()
        AFTER_DOCTYPE_SYSTEM_KEYWORD                  = _auto()
        BEFORE_DOCTYPE_SYSTEM_IDENTIFIER              = _auto()
        DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED       = _auto()
        DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED       = _auto()
        AFTER_DOCTYPE_SYSTEM_IDENTIFIER               = _auto()
        BOGUS_DOCTYPE                                 = _auto()
        CDATA_SECTION                                 = _auto()
        CDATA_SECTION_BRACKET                         = _auto()
        CDATA_SECTION_END                             = _auto()
        CHARACTER_REFERENCE                           = _auto()
        NAMED_CHARACTER_REFERENCE                     = _auto()
        AMBIGUOUS_AMPERSAND                           = _auto()
        NUMERIC_CHARACTER_REFERENCE                   = _auto()
        HEXADECIMAL_CHARACTER_REFERENCE_START         = _auto()
        DECIMAL_CHARACTER_REFERENCE_START             = _auto()
        HEXADECIMAL_CHARACTER_REFERENCE               = _auto()
        DECIMAL_CHARACTER_REFERENCE                   = _auto()
        NUMERIC_CHARACTER_REFERENCE_END               = _auto()
        
        
    whitespace  = "\t\n\f " 
    ascii_alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def __init__(self):
        
        # states
        self.state = self.State.DATA
        self.return_state: self.State = None
        
        self.temporary_buffer = None
        self.last_emitted_start_tag_name = ""
        
        # current token (to emit)
        self.curr_token: HTMLToken = None
        
        # current char index
        self.i = 0
        
    
    def _switch_to(self, state: "HTMLTokenizer.State"):
        
        self.state = state
    

    def _reconsume_in(self, state: "HTMLTokenizer.State"):
        
        self.state = state
        self.i -= 1
            
    
    def _set_return(self, state: "HTMLTokenizer.State"):
        
        self.return_state = state
        
    
    def _emit_token(self, token: HTMLToken = None) -> HTMLToken:
        
        if token: self.curr_token = token # shortcut
        
        # store last emitted start tag name
        # to check if appropriate end tag token
        if self.curr_token.type == HTMLToken.Type.START_TAG:
            self.last_emitted_start_tag_name = self.curr_token.tag_name
        
        temp_tok = self.curr_token
        self.curr_token = None
        return temp_tok
    

    def _parse_error(self, code: str):
        
        print("Parse Error:", code)
        
    
    def run(self, html_text: str) -> _Generator[HTMLToken, None, None]:
        
        html_text = html_text.strip()
        
        self.i = 0
        while self.i <= len(html_text):
            
            is_eof = (self.i == len(html_text))
            
            c = ""
            if is_eof:
                c = "EOF" # will not be used
            else:
                # consume the current input char
                c = html_text[self.i]
                self.i += 1
            
            if self.state == self.State.DATA:
                
                if c == "&":
                    self._set_return(self.State.DATA)
                    self._switch_to(self.State.CHARACTER_REFERENCE)
                
                elif c == "<":
                    self._switch_to(self.State.TAG_OPEN)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    yield self._emit_token(HTMLTokenCharacter(c))
                
                elif is_eof:
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    yield self._emit_token(HTMLTokenCharacter(c))
                
            elif self.state == self.State.RCDATA:
                
                if c == "&":
                    self._set_return(self.State.DATA)
                    self._switch_to(self.State.CHARACTER_REFERENCE)
                
                elif c == "<":
                    self._switch_to(self.State.RCDATA_LESS_THAN_SIGN)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                
                elif is_eof:
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    yield self._emit_token(HTMLTokenCharacter(c))
                
            elif self.state == self.State.RAWTEXT:
                
                if c == "<":
                    self._switch_to(self.State.RAWTEXT_LESS_THAN_SIGN)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                
                elif is_eof:
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    yield self._emit_token(HTMLTokenCharacter(c))
                
            elif self.state == self.State.SCRIPT_DATA:
                
                if c == "<":
                    self._switch_to(self.State.SCRIPT_DATA_LESS_THAN_SIGN)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                
                elif is_eof:
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    yield self._emit_token(HTMLTokenCharacter(c))
                
            elif self.state == self.State.PLAIN_TEXT:
                
                if c == "\0":
                    self._parse_error("unexpected-null-character")
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                
                elif is_eof:
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    yield self._emit_token(HTMLTokenCharacter(c))
            
            elif self.state == self.State.TAG_OPEN:
                
                if c == "!":
                    self._switch_to(self.State.MARKUP_DECLARATION_OPEN)
                    
                elif c == "/":
                    self._switch_to(self.State.END_TAG_OPEN)
                    
                elif c in self.ascii_alpha:
                    self.curr_token = HTMLTokenStartTag()
                    self.curr_token.tag_name = ""
                    self._reconsume_in(self.State.TAG_NAME)

                elif c == "?":
                    self._parse_error("unexpected-question-mark-instead-of-tag-name")
                    self.curr_token = HTMLTokenComment("")
                    self._reconsume_in(self.State.BOGUS_COMMENT)
                
                elif is_eof:
                    self._parse_error("eof-before-tag-name")
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("invalid-first-character-of-tag-name")
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    self._reconsume_in(self.State.DATA)
                    
            elif self.state == self.State.END_TAG_OPEN:
                
                if c in self.ascii_alpha:
                    self.curr_token = HTMLTokenEndTag()
                    self.curr_token.tag_name = ""
                    self._reconsume_in(self.State.TAG_NAME)
                    
                elif c == ">":
                    self._parse_error("missing-end-tag-name")
                    self._switch_to(self.State.DATA)
                
                elif is_eof:
                    self._parse_error("eof-before-tag-name")
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenCharacter("/"))
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("invalid-first-character-of-tag-name")
                    self.curr_token = HTMLTokenComment("")
                    self._reconsume_in(self.State.BOGUS_COMMENT)
            
            elif self.state == self.State.TAG_NAME:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                
                elif c == "/":
                    self._switch_to(self.State.SELF_CLOSING_START_TAG)
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif c == "\0":
                    self._parse_error("unexpected-question-mark-instead-of-tag-name")
                    self.curr_token.tag_name += u"\ufffd"
                
                elif is_eof:
                    self._parse_error("eof-in-tag")
                    self._emit_token(HTMLTokenEOF())
                
                else:
                    self.curr_token.tag_name += c.lower()
                    
            elif self.state == self.State.RCDATA_LESS_THAN_SIGN:
                
                if c == "/":
                    self.temporary_buffer = ""
                    self._switch_to(self.State.RCDATA_END_TAG_OPEN)
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    self._reconsume_in(self.RCDATA)
                
            elif self.state == self.State.RCDATA_END_TAG_OPEN:
                
                if c in self.ascii_alpha:
                    self.curr_token = HTMLTokenEndTag()
                    self.curr_token.tag_name = ""
                    self._reconsume_in(self.State.RCDATA_END_TAG_NAME)
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenCharacter("/"))
                    self._reconsume_in(self.RCDATA)
                
            elif self.state == self.State.RCDATA_END_TAG_NAME:
                
                if c in self.whitespace:
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.RCDATA)
                        
                elif c == "/":
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.SELF_CLOSING_START_TAG)
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.RCDATA)
                        
                elif c == ">":
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.DATA)
                        yield self._emit_token()
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.RCDATA)
                
                elif c in self.ascii_alpha:
                    self.curr_token.tag_name += c.lower()
                    self.temporary_buffer += c
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenCharacter("/"))
                    while len(self.temporary_buffer):
                        # pop first char of temporary buffer
                        c_ = self.temporary_buffer[0]
                        self.temporary_buffer = self.temporary_buffer[1:]
                        yield self._emit_token(HTMLTokenCharacter(c_))
                    self._reconsume_in(self.State.RCDATA)
                    
            elif self.state == self.State.RAWTEXT_LESS_THAN_SIGN:
                
                if c == "/":
                    self.temporary_buffer = ""
                    self._switch_to(self.State.RAWTEXT_END_TAG_OPEN)
                
                else:
                   yield self._emit_token(HTMLTokenCharacter("<"))
                   self._reconsume_in(self.State.RAWTEXT)
               
            elif self.state == self.State.RAWTEXT_END_TAG_OPEN:
                
                if c in self.ascii_alpha:
                    self.curr_token = HTMLTokenEndTag()
                    self.curr_token.tag_name = ""
                    self._reconsume_in(self.State.RAWTEXT_END_TAG_NAME)
                
                else:
                   yield self._emit_token(HTMLTokenCharacter("<"))
                   yield self._emit_token(HTMLTokenCharacter("/"))
                   self._reconsume_in(self.State.RAWTEXT)
            
            elif self.state == self.State.RAWTEXT_END_TAG_NAME:
                
                if c in self.whitespace:
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.RAWTEXT)
                
                elif c == "/":
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.SELF_CLOSING_START_TAG)
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.RAWTEXT)
                
                elif c == ">":
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.DATA)
                        yield self._emit_token()
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.RAWTEXT)
                
                elif c in self.ascii_alpha:
                    self.curr_token.tag_name += c.lower()
                    self.temporary_buffer += c
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenCharacter("/"))
                    while len(self.temporary_buffer):
                        # pop first char of temporary buffer
                        c_ = self.temporary_buffer[0]
                        self.temporary_buffer = self.temporary_buffer[1:]
                        yield self._emit_token(HTMLTokenCharacter(c_))
                    self._reconsume_in(self.State.RAWTEXT)
            
            elif self.state == self.State.SCRIPT_DATA_LESS_THAN_SIGN:
                
                if c == "/":
                    self.temporary_buffer = ""
                    self._switch_to(self.State.SCRIPT_DATA_END_TAG_OPEN)
                
                elif c == "!":
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPE_START)
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenCharacter("!"))

                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    self._reconsume_in(self.State.SCRIPT_DATA)
                    
            elif self.state == self.State.SCRIPT_DATA_END_TAG_OPEN:
                
                if c in self.ascii_alpha:
                    self.curr_token = HTMLTokenEndTag()
                    self.curr_token.tag_name = ""
                    self._reconsume_in(self.State.SCRIPT_DATA_END_TAG_NAME)
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenCharacter("/"))
                    self._reconsume_in(self.State.SCRIPT_DATA)
                
            elif self.state == self.State.SCRIPT_DATA_END_TAG_NAME:
                
                if c in self.whitespace:
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.SCRIPT_DATA)
                
                elif c == "/":
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.SELF_CLOSING_START_TAG)
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.SCRIPT_DATA)
                
                elif c == ">":
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.DATA)
                        yield self._emit_token()
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.SCRIPT_DATA)
                
                elif c in self.ascii_alpha:
                    self.curr_token.tag_name += c.lower()
                    self.temporary_buffer += c
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenCharacter("/"))
                    while len(self.temporary_buffer):
                        # pop first char of temporary buffer
                        c_ = self.temporary_buffer[0]
                        self.temporary_buffer = self.temporary_buffer[1:]
                        yield self._emit_token(HTMLTokenCharacter(c_))
                    self._reconsume_in(self.State.SCRIPT_DATA)
            
            elif self.state == self.State.SCRIPT_DATA_ESCAPE_START:
                
                if c == "-":
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPE_START_DASH)
                    yield self._emit_token(HTMLTokenCharacter("-"))
                
                else:
                    self._reconsume_in(self.State.SCRIPT_DATA)
            
            elif self.state == self.State.SCRIPT_DATA_ESCAPE_START_DASH:
                
                if c == "-":
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED_DASH_DASH)
                    yield self._emit_token(HTMLTokenCharacter("-"))
                
                else:
                    self._reconsume_in(self.State.SCRIPT_DATA)
            
            elif self.state == self.State.SCRIPT_DATA_ESCAPED:
                
                if c == "-":
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED_DASH)
                    yield self._emit_token(HTMLTokenCharacter("-"))

                elif c == "<":
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN)

                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                    
                elif is_eof:
                    self._parse_error("eof-in-script-html-comment-like-text")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    yield self._emit_token(HTMLTokenCharacter(c))
                
            elif self.state == self.State.SCRIPT_DATA_ESCAPED_DASH:
                
                if c == "-":
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED_DASH_DASH)
                    yield self._emit_token(HTMLTokenCharacter("-"))

                elif c == "<":
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN)

                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED)
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                
                elif is_eof:
                    self._parse_error("eof-in-script-html-comment-like-text")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED)
                    yield self._emit_token(HTMLTokenCharacter(c))
                
            elif self.state == self.State.SCRIPT_DATA_ESCAPED_DASH_DASH:
                
                if c == "-":
                    yield self._emit_token(HTMLTokenCharacter("-"))

                elif c == "<":
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN)

                elif c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token(HTMLTokenCharacter(">"))

                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED)
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                
                elif is_eof:
                    self._parse_error("eof-in-script-html-comment-like-text")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED)
                    yield self._emit_token(HTMLTokenCharacter(c))
                
            elif self.state == self.State.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN:
                
                if c == "/":
                    self.temporary_buffer = ""
                    self._switch_to(self.State.SCRIPT_DATA_ESCAPED_END_TAG_OPEN)
                
                elif c in self.ascii_alpha:
                    self.temporary_buffer = ""
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    self._reconsume_in(self.State.SCRIPT_DATA_DOUBLE_ESCAPE_START)
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    self._reconsume_in(self.State.SCRIPT_DATA_ESCAPED)
                    
            elif self.state == self.State.SCRIPT_DATA_ESCAPED_END_TAG_OPEN:
                
                if c in self.ascii_alpha:
                    self.curr_token = HTMLTokenEndTag()
                    self.curr_token.tag_name = ""
                    self._reconsume_in(self.State.SCRIPT_DATA_ESCAPED_END_TAG_NAME)
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenCharacter("/"))
                    self._reconsume_in(self.State.SCRIPT_DATA_ESCAPED)
            
            elif self.state == self.State.SCRIPT_DATA_ESCAPED_END_TAG_NAME:
                
                if c in self.whitespace:
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.SCRIPT_DATA_ESCAPED)
                
                elif c == "/":
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.SELF_CLOSING_START_TAG)
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.SCRIPT_DATA_ESCAPED)
                
                elif c == ">":
                    # if the current end token is an appropriate end tag token
                    if self.curr_token.tag_name == self.last_emitted_start_tag_name:
                        self._switch_to(self.State.DATA)
                        yield self._emit_token()
                    
                    else:
                        yield self._emit_token(HTMLTokenCharacter("<"))
                        yield self._emit_token(HTMLTokenCharacter("/"))
                        while len(self.temporary_buffer):
                            # pop first char of temporary buffer
                            c_ = self.temporary_buffer[0]
                            self.temporary_buffer = self.temporary_buffer[1:]
                            yield self._emit_token(HTMLTokenCharacter(c_))
                        self._reconsume_in(self.State.SCRIPT_DATA_ESCAPED)
                
                elif c in self.ascii_alpha:
                    self.curr_token.tag_name += c.lower()
                    self.temporary_buffer += c
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("<"))
                    yield self._emit_token(HTMLTokenCharacter("/"))
                    while len(self.temporary_buffer):
                        # pop first char of temporary buffer
                        c_ = self.temporary_buffer[0]
                        self.temporary_buffer = self.temporary_buffer[1:]
                        yield self._emit_token(HTMLTokenCharacter(c_))
                    self._reconsume_in(self.State.SCRIPT_DATA_ESCAPED)
            
            elif self.state == self.State.SCRIPT_DATA_DOUBLE_ESCAPE_START:
                
                if c in self.whitespace:
                    if self.temporary_buffer == "script":
                        self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED)
                    else:
                        self._switch_to(self.State.SCRIPT_DATA_ESCAPED)
                        yield self._emit_token(HTMLTokenCharacter(c))
                
                elif c in self.ascii_alpha:
                    self.temporary_buffer += c.lower()
                    yield self._emit_token(HTMLTokenCharacter(c))
                
                else:
                    self._reconsume_in(self.State.SCRIPT_DATA_ESCAPED)
                        
            elif self.state == self.State.SCRIPT_DATA_DOUBLE_ESCAPED:
                
                if c == "-":
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED_DASH)
                    yield self._emit_token(HTMLTokenCharacter("-"))
                
                elif c == "<":
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN)
                    yield self._emit_token(HTMLTokenCharacter("<"))
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                
                elif is_eof:
                    self._parse_error("eof-in-script-html-comment-like-text")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    yield self._emit_token(HTMLTokenCharacter(c))
                        
            elif self.state == self.State.SCRIPT_DATA_DOUBLE_ESCAPED_DASH:
                
                if c == "-":
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH)
                    yield self._emit_token(HTMLTokenCharacter("-"))
                
                elif c == "<":
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN)
                    yield self._emit_token(HTMLTokenCharacter("<"))
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED)
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                
                elif is_eof:
                    self._parse_error("eof-in-script-html-comment-like-text")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED)
                    yield self._emit_token(HTMLTokenCharacter(c))
                        
            elif self.state == self.State.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH:
                
                if c == "-":
                    yield self._emit_token(HTMLTokenCharacter("-"))
                
                elif c == "<":
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN)
                    yield self._emit_token(HTMLTokenCharacter("<"))
                
                elif c == ">":
                    self._switch_to(self.State.SCRIPT_DATA)
                    yield self._emit_token(HTMLTokenCharacter(">"))
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED)
                    yield self._emit_token(HTMLTokenCharacter(u"\ufffd"))
                
                elif is_eof:
                    self._parse_error("eof-in-script-html-comment-like-text")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED)
                    yield self._emit_token(HTMLTokenCharacter(c))
                    
            elif self.state == self.State.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN:
                
                if c == "/":
                    self.temporary_buffer = ""
                    self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPE_END)
                    yield self._emit_token(HTMLTokenCharacter("/"))
                
                else:
                    self._reconsume_in(self.State.SCRIPT_DATA_DOUBLE_ESCAPED)
            
            elif self.state == self.State.SCRIPT_DATA_DOUBLE_ESCAPE_END:
                
                if c in self.whitespace:
                    if self.temporary_buffer == "script":
                        self._switch_to(self.State.SCRIPT_DATA_ESCAPED)

                    else:
                        self._switch_to(self.State.SCRIPT_DATA_DOUBLE_ESCAPED)
                        yield self._emit_token(HTMLTokenCharacter(c))
                
                elif c in self.ascii_alpha:
                    self.temporary_buffer += c.lower()
                    yield self._emit_token(HTMLTokenCharacter(c))
                
                else:
                    self._reconsume_in(self.State.SCRIPT_DATA_DOUBLE_ESCAPED)
            
            elif self.state == self.State.BEFORE_ATTRIBUTE_NAME:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c in "/>" or is_eof:
                    self._reconsume_in(self.State.AFTER_ATTRIBUTE_NAME)
                
                elif c == "=":
                    self._parse_error("unexpected-equals-sign-before-attribute-name")
                    self.curr_token.attributes.append([c, ""])
                    self._switch_to(self.State.ATTRIBUTE_NAME)
                    
                else:
                    self.curr_token.attributes.append(["", "" ])
                    self._reconsume_in(self.State.ATTRIBUTE_NAME)
            
            elif self.state == self.State.ATTRIBUTE_NAME:
                
                if c in self.whitespace or c in "/>" or is_eof:
                    self._reconsume_in(self.State.AFTER_ATTRIBUTE_NAME)
                
                elif c == "=":
                    self._switch_to(self.State.BEFORE_ATTRIBUTE_VALUE)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.attributes[-1][0] += u"\ufffd"
                    assert 0, "NOT IMPLEMENTED"
                
                elif c in "\"'<":
                    self._parse_error("unexpected-character-in-attribute-name")
                    self.curr_token.attributes[-1][0] += c.lower()
                
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
                    yield self._emit_token()
                    
                elif is_eof:
                    self._parse_error("eof-in-tag")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self.curr_token.attributes.append(["", "" ])
                    self._reconsume_in(self.State.ATTRIBUTE_NAME)
                    
            elif self.state == self.State.BEFORE_ATTRIBUTE_VALUE:
                
                if c in self.whitespace:
                    pass # ignore 
                
                elif c == "\"":
                    self._switch_to(self.State.ATTRIBUTE_VALUE_DOUBLE_QUOTED)
                
                elif c == "'":
                    self._switch_to(self.State.ATTRIBUTE_VALUE_SINGLE_QUOTED)
                
                elif c == ">":
                    self._parse_error("missing-attribute-value")
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                    
                else:
                    self._reconsume_in(self.State.ATTRIBUTE_VALUE_UNQUOTED)

            elif self.state == self.State.ATTRIBUTE_VALUE_DOUBLE_QUOTED:
                
                if c == "\"":
                    self._switch_to(self.State.AFTER_ATTRIBUTE_VALUE_QUOTED)
                    
                elif c == "&":
                    self._set_return(self.State.ATTRIBUTE_VALUE_DOUBLE_QUOTED)
                    self._switch_to(self.State.CHARACTER_REFERENCE)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.attributes[-1][1] += u"\ufffd"
                
                elif is_eof:
                    self._parse_error("eof-in-tag")
                    yield self._emit_token(HTMLTokenEOF())
                    
                else:
                    self.curr_token.attributes[-1][1] += c
            
            elif self.state == self.State.ATTRIBUTE_VALUE_SINGLE_QUOTED:
                
                if c == "'":
                    self._switch_to(self.State.AFTER_ATTRIBUTE_VALUE_QUOTED)
                    
                elif c == "&":
                    self._set_return(self.State.ATTRIBUTE_VALUE_SINGLE_QUOTED)
                    self._switch_to(self.State.CHARACTER_REFERENCE)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.attributes[-1][1] += u"\ufffd"
                
                elif is_eof:
                    self._parse_error("eof-in-tag")
                    yield self._emit_token(HTMLTokenEOF())
                    
                else:
                    self.curr_token.attributes[-1][1] += c
            
            elif self.state == self.State.ATTRIBUTE_VALUE_UNQUOTED:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                    
                elif c == "&":
                    self._set_return(self.State.ATTRIBUTE_VALUE_UNQUOTED)
                    self._switch_to(self.State.CHARACTER_REFERENCE)

                elif c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()

                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.attributes[-1][1] += u"\ufffd"
                    
                elif c in "\"'<=`":
                    self._parse_error("unexpected-character-in-unquoted-attribute-value")
                    self.curr_token.attributes[-1][1] += c
                
                elif is_eof:
                    self._parse_error("eof-in-tag")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self.curr_token.attributes[-1][1] += c
            
            elif self.state == self.State.AFTER_ATTRIBUTE_VALUE_QUOTED:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_ATTRIBUTE_NAME)
                    
                elif c == "/":
                    self._switch_to(self.State.SELF_CLOSING_START_TAG)
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-tag")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("missing-whitespace-between-attributes")
                    self._reconsume_in(self.State.BEFORE_ATTRIBUTE_NAME)
            
            elif self.state == self.State.SELF_CLOSING_START_TAG:
                
                if c == ">":
                    self.curr_token.self_closing_tag = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-tag")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("unexpected-solidus-in-tag")
                    self._reconsume_in(self.State.BEFORE_ATTRIBUTE_NAME)
                    
            # HELP ME!
            
            elif self.state == self.State.BOGUS_COMMENT:
                
                if c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # comment token
                    
                elif is_eof:
                    yield self._emit_token() # comment token
                    yield self._emit_token(HTMLTokenEOF()) # comment token
                
                else:
                    self.curr_token.data += c
                    
            elif self.state == self.State.MARKUP_DECLARATION_OPEN:
                
                if html_text[self.i-1:self.i+1] == "--":
                    self.curr_token = HTMLTokenComment("")
                    self._switch_to(self.State.COMMENT_START)
                    self.i += 1 # consume also the second "-"
                
                elif self.i+5 < len(html_text) and html_text[self.i-1:self.i+6].upper() == "DOCTYPE":
                    self._switch_to(self.State.DOCTYPE)
                    self.i += 6 # consume also the rest "OCTYPE" 
                
                elif self.i+5 < len(html_text) and html_text[self.i-1:self.i+6] == "[CDATA[":
                    assert 0, "NOT IMPLEMENTED"
                    # TODO: see https://html.spec.whatwg.org/multipage/parsing.html#markup-declaration-open-state
                    self.i += 6 # consume also the rest "CDATA[" 
                
                else:
                    self._parse_error("incorrectly-opened-comment")
                    self.curr_token = HTMLTokenComment("")
                    self._reconsume_in(self.State.BOGUS_COMMENT)
                    # TODO: is this reconsume or switch I could not get it
                    # see https://html.spec.whatwg.org/multipage/parsing.html#markup-declaration-open-state
            
            elif self.state == self.State.COMMENT_START:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_START_DASH)
                
                elif c == ">":
                    self._parse_error("abrupt-closing-of-empty-comment")
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # comment token
                    
                else:
                    self._reconsume_in(self.State.COMMENT)
                    
            elif self.state == self.State.COMMENT_START_DASH:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_END)
                
                elif c == ">":
                    self._parse_error("abrupt-closing-of-empty-comment")
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # comment token
                
                elif is_eof:
                    self._parse_error("eof-in-comment")
                    yield self._emit_token() # comment token
                    yield self._emit_token(HTMLTokenEOF())

                else:
                    self.curr_token.data += "-"
                    self._reconsume_in(self.State.COMMENT)
                    
            elif self.state == self.State.COMMENT:
                
                if c == "<":
                    self.curr_token.data += c
                    self._switch_to(self.State.COMMENT_LESS_THAN_SIGN)
                
                elif c == "-":
                    self._switch_to(self.State.COMMENT_END_DASH)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.data += u"\ufffd"
                
                elif is_eof:
                    self._parse_error("eof-in-comment")
                    yield self._emit_token() # comment token
                    yield self._emit_token(HTMLTokenEOF())
                    
                else:
                    self.curr_token.data += c
            
            elif self.state == self.State.COMMENT_LESS_THAN_SIGN:
                
                if c == "!":
                    self.curr_token.data += c
                    self._switch_to(self.State.COMMENT_LESS_THAN_SIGN_BANG)
                
                elif c == "<":
                    self.curr_token.data += c 
                
                else:
                    self._reconsume_in(self.State.COMMENT)
            
            elif self.state == self.State.COMMENT_LESS_THAN_SIGN_BANG:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_LESS_THAN_SIGN_BANG_DASH)
                
                else:
                    self._reconsume_in(self.State.COMMENT)
                    
            elif self.state == self.State.COMMENT_LESS_THAN_SIGN_BANG_DASH:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH)
                
                else:
                    self._reconsume_in(self.State.COMMENT_END_DASH)
                    
            elif self.state == self.State.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH:
                
                if c == ">" or is_eof:
                    self._reconsume_in(self.State.COMMENT_END)
                
                else:
                    self._parse_error("nested-comment")
                    self._reconsume_in(self.State.COMMENT_END)
                    
            elif self.state == self.State.COMMENT_END_DASH:
                
                if c == "-":
                    self._switch_to(self.State.COMMENT_END)
                
                elif is_eof:
                    self._parse_error("eof-in-comment")
                    yield self._emit_token() # comment token
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self.curr_token.data += "-"
                    self._reconsume_in(self.State.COMMENT)
                    
            elif self.state == self.State.COMMENT_END:
                
                if c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()

                elif c == "!":
                    self._switch_to(self.State.COMMENT_END_BANG)
                
                elif c == "-":
                    self.curr_token.data += "-"
                    
                elif is_eof:
                    self._parse_error("eof-in-comment")
                    yield self._emit_token() # comment token
                    yield self._emit_token(HTMLTokenEOF())
                    
                else:
                    self.curr_token.data += "--"
                    self._reconsume_in(self.State.COMMENT)
                    
            elif self.state == self.State.COMMENT_END_BANG:
                
                if c == "-":
                    self.curr_token.data += "--!"
                    self._switch_to(self.State.COMMENT_END_DASH)
                
                elif c == ">":
                    self._parse_error("incorrectly-closed-comment")
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # comment token
                    
                elif is_eof:
                    self._parse_error("eof-in-comment")
                    yield self._emit_token() # comment token
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self.curr_token.data += "--!"
                    self.return_state(self.State.COMMENT)
            
            elif self.state == self.State.DOCTYPE:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_DOCTYPE_NAME)
                
                elif c == ">":
                    self._reconsume_in(self.State.BEFORE_DOCTYPE_NAME)
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token = HTMLTokenDoctype()
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("missing-whitespace-before-doctype-name")
                    self._reconsume_in(self.State.BEFORE_DOCTYPE_NAME)
                    
            elif self.state == self.State.BEFORE_DOCTYPE_NAME:
                
                if c in self.whitespace:
                    pass # ignore
                    
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token = HTMLTokenDoctype()
                    self.curr_token.name = u"\ufffd"
                    self._switch_to(self.State.DOCTYPE_NAME)
                    
                elif c == ">":
                    self._parse_error("missing-doctype-name")
                    self.curr_token = HTMLTokenDoctype()
                    self.curr_token.force_quirks = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token = HTMLTokenDoctype()
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                                    
                else:
                    self.curr_token = HTMLTokenDoctype()
                    self.curr_token.name = c.lower()
                    self._switch_to(self.State.DOCTYPE_NAME)
            
            elif self.state == self.State.DOCTYPE_NAME:
            
                if c in self.whitespace:
                    self._switch_to(self.State.AFTER_DOCTYPE_NAME)
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # doctype token
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.name += u"\ufffd"
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                    
                else:
                    self.curr_token.name += c.lower()
            
            elif self.state == self.State.AFTER_DOCTYPE_NAME:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                
                    if self.i+4 < len(html_text) and html_text[self.i-1:self.i+5].upper() == "PUBLIC":
                        self._switch_to(self.State.AFTER_DOCTYPE_PUBLIC_KEYWORD)
                        self.i += 5 # consume the rest "UBLIC"
                    
                    elif self.i+4 < len(html_text) and html_text[self.i-1:self.i+5].upper() == "SYSTEM":
                        self._switch_to(self.State.AFTER_DOCTYPE_SYSTEM_KEYWORD)
                        self.i += 5 # consume the rest "YSTEM"
                    
                    else:
                        self._parse_error("invalid-character-sequence-after-doctype-name")
                        self.curr_token.force_quirks = 1
                        self._reconsume_in(self.State.BOGUS_DOCTYPE)
                        
            elif self.state == self.State.AFTER_DOCTYPE_PUBLIC_KEYWORD:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER)
                
                elif c == "\"":
                    self._parse_error("missing-whitespace-after-doctype-public-keyword")
                    self.curr_token.public_identifier = ""
                    self._switch_to(self.State.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED)
                
                elif c == "'":
                    self._parse_error("missing-whitespace-after-doctype-public-keyword")
                    self.curr_token.public_identifier = ""
                    self._switch_to(self.State.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED)
                    
                elif c == ">":
                    self._parse_error("missing-doctype-public-identifier")
                    self.curr_token.force_quirks = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("missing-quote-before-doctype-public-identifier")
                    self.curr_token.force_quirks = 1
                    self._reconsume_in(self.State.BOGUS_DOCTYPE)
            
            elif self.state == self.State.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c == "\"":
                    self.curr_token.public_identifier = ""
                    self._switch_to(self.State.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED)
                
                elif c == "'":
                    self.curr_token.public_identifier = ""
                    self._switch_to(self.State.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED)
                    
                elif c == ">":
                    self._parse_error("missing-doctype-public-identifier")
                    self.curr_token.force_quirks = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("missing-quote-before-doctype-public-identifier")
                    self.curr_token.force_quirks = 1
                    self._reconsume_in(self.State.BOGUS_DOCTYPE)
                
            elif self.state == self.State.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED:
                
                if c == "\"":
                    self._switch_to(self.State.AFTER_DOCTYPE_PUBLIC_IDENTIFIER)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.public_identifier += u"\ufffd"
                
                elif c == ">":
                    self._parse_error("abrupt-doctype-public-identifier")
                    self.curr_token.force_quirks = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                    
                else:
                    self.curr_token.public_identifier += c
                    
            elif self.state == self.State.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED:
                
                if c == "'":
                    self._switch_to(self.State.AFTER_DOCTYPE_PUBLIC_IDENTIFIER)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.public_identifier += u"\ufffd"
                
                elif c == ">":
                    self._parse_error("abrupt-doctype-public-identifier")
                    self.curr_token.force_quirks = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self.curr_token.public_identifier += c
            
            elif self.state == self.State.AFTER_DOCTYPE_PUBLIC_IDENTIFIER:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS)
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # doctype token
                
                elif c == "\"":
                    self._parse_error("missing-whitespace-between-doctype-public-and-system-identifiers")
                    self.curr_token.system_identifier = ""
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED)
                
                elif c == "'":
                    self._parse_error("missing-whitespace-between-doctype-public-and-system-identifiers")
                    self.curr_token.system_identifier = ""
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED)
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                    
                else:
                    self._parse_error("missing-quote-before-doctype-system-identifier")
                    self.curr_token.force_quirks = 1
                    self._reconsume_in(self.State.BOGUS_DOCTYPE)
                    
            elif self.state == self.State.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # doctype token
                
                elif c == "\"":
                    self.curr_token.system_identifier = ""
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED)
                
                elif c == "'":
                    self.curr_token.system_identifier = ""
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED)
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("missing-quote-before-doctype-system-identifier")
                    self.curr_token.force_quirks = 1
                    self._reconsume_in(self.State.BOGUS_DOCTYPE)
                    
            elif self.state == self.State.AFTER_DOCTYPE_SYSTEM_KEYWORD:
                
                if c in self.whitespace:
                    self._switch_to(self.State.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER)
                
                elif c == "\"":
                    self._parse_error("missing-whitespace-after-doctype-system-keyword")
                    self.curr_token.system_identifier = ""
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED)
                
                elif c == "'":
                    self._parse_error("missing-whitespace-after-doctype-system-keyword")
                    self.curr_token.system_identifier = ""
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED)
                
                elif c == ">":
                    self._parse_error("missing-doctype-system-identifier")
                    self.curr_token.force_quirks = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("missing-quote-before-doctype-system-identifier")
                    self.curr_token.force_quirks = 1
                    self._reconsume_in(self.State.BOGUS_DOCTYPE)
                    
            elif self.state == self.State.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER:
                
                if c in self.whitespace:
                    pass # ignore
                
                elif c == "\"":
                    self.curr_token.system_identifier = ""
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED)
                
                elif c == "'":
                    self.curr_token.system_identifier = ""
                    self._switch_to(self.State.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED)
                
                elif c == ">":
                    self._parse_error("missing-doctype-system-identifier")
                    self.curr_token.force_quirks = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # doctype token
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("missing-quote-before-doctype-system-identifier")
                    self.curr_token.force_quirks = 1
                    self._reconsume_in(self.State.BOGUS_DOCTYPE)
                    
            elif self.state == self.State.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED:
                
                if c == "\"":
                    self._switch_to(self.State.AFTER_DOCTYPE_SYSTEM_IDENTIFIER)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.system_identifier = u"\ufffd"
                
                elif c == ">":
                    self._parse_error("abrupt-doctype-system-identifier")
                    self.curr_token.force_quirks = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                    
                else:
                    self.curr_token.system_identifier += c
                    
            elif self.state == self.State.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED:
                
                if c == "'":
                    self._switch_to(self.State.AFTER_DOCTYPE_SYSTEM_IDENTIFIER)
                
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    self.curr_token.system_identifier = u"\ufffd"
                
                elif c == ">":
                    self._parse_error("abrupt-doctype-system-identifier")
                    self.curr_token.force_quirks = 1
                    self._switch_to(self.State.DATA)
                    yield self._emit_token()
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                    
                else:
                    self.curr_token.system_identifier += c
                    
            elif self.state == self.State.AFTER_DOCTYPE_SYSTEM_IDENTIFIER:
                
                if c in self.whitespace:
                    pass # ignore
                    
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # doctype token
                
                elif is_eof:
                    self._parse_error("eof-in-doctype")
                    self.curr_token.force_quirks = 1
                    yield self._emit_token()
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    self._parse_error("unexpected-character-after-doctype-system-identifier")
                    self._reconsume_in(self.State.BOGUS_DOCTYPE)
            
            elif self.state == self.State.BOGUS_COMMENT:
                
                if c == ">":
                    self._switch_to(self.State.DATA)
                    yield self._emit_token() # doctype token
                    
                elif c == "\0":
                    self._parse_error("unexpected-null-character")
                    pass # ignore
            
                elif is_eof:
                    yield self._emit_token() # doctype token
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    pass # ignore
            
            elif self.state == self.State.CDATA_SECTION:
                
                if c == "]":
                    self._switch_to(self.State.CDATA_SECTION_BRACKET)
                
                elif is_eof:
                    self._parse_error("eof-in-cdata")
                    yield self._emit_token(HTMLTokenEOF())
                
                else:
                    yield self._emit_token(HTMLTokenCharacter(c))
            
            elif self.state == self.State.CDATA_SECTION_BRACKET:
                
                if c == "]":
                    self._switch_to(self.State.CDATA_SECTION_END)
                
                else:
                    yield self._emit_token(HTMLTokenCharacter("]"))
                    self._reconsume_in(self.State.CDATA_SECTION)
            
            elif self.state == self.State.CDATA_SECTION_END:
            
                if c == "]":
                    yield self._emit_token(HTMLTokenCharacter("]"))
                    
                elif c == ">":
                    self._switch_to(self.State.DATA)
                    
                else:
                    yield self._emit_token(HTMLTokenCharacter("]"))
                    yield self._emit_token(HTMLTokenCharacter("]"))
                    self._reconsume_in(self.State.CDATA_SECTION)
            
            elif self.state == self.State.CHARACTER_REFERENCE:
                assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.NAMED_CHARACTER_REFERENCE:
                assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.AMBIGUOUS_AMPERSAND:
                assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.NUMERIC_CHARACTER_REFERENCE:
                assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.HEXADECIMAL_CHARACTER_REFERENCE_START:
                assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.DECIMAL_CHARACTER_REFERENCE_START:
                assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.HEXADECIMAL_CHARACTER_REFERENCE:
                assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.DECIMAL_CHARACTER_REFERENCE:
                assert 0, "NOT IMPLEMENTED"
            
            elif self.state == self.State.NUMERIC_CHARACTER_REFERENCE_END:
                assert 0, "NOT IMPLEMENTED"
            
            else:
                assert 0, "UNREACHABLE"
            