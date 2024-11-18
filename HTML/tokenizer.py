from .token import HTMLTokenType, HTMLToken


class HTMLTokenizer:
    
    # tag    
    OPEN_TAG_SYMBOL  = "<"
    CLOSE_TAG_SYMBOL = ">"
    SLASH_SYMBOL     = "/"
    
    # attr
    EQUALS_SYMBOL       = "="
    SINGLE_QUOTE_SYMBOL = "'"
    DOUBLE_QUOTE_SYMBOL = "\""
    
    ALL_SYMBOLS = OPEN_TAG_SYMBOL+CLOSE_TAG_SYMBOL+SLASH_SYMBOL\
        +EQUALS_SYMBOL+SINGLE_QUOTE_SYMBOL+DOUBLE_QUOTE_SYMBOL
    
    whitespace = " \t\n\r\x0b\x0c"
    
    def __init__(self):
        
        pass
    
    
    def run(self, html_text: str) -> list[HTMLToken]:
        
        print(html_text)
        
        tokens: list[HTMLToken] = []
        
        i = 0
        curr_text = ""
        while i < len(html_text):
            c = html_text[i]
            
            if c == self.OPEN_TAG_SYMBOL:
                tokens.append(HTMLToken(HTMLTokenType.OPEN_TAG, None))
            
            elif c == self.CLOSE_TAG_SYMBOL:
                tokens.append(HTMLToken(HTMLTokenType.CLOSE_TAG, None))
                
            elif c == self.SLASH_SYMBOL:
                tokens.append(HTMLToken(HTMLTokenType.SLASH, None))
                
            elif c == self.EQUALS_SYMBOL:
                tokens.append(HTMLToken(HTMLTokenType.EQUALS, None))
                
            elif c == self.SINGLE_QUOTE_SYMBOL:
                tokens.append(HTMLToken(HTMLTokenType.SINGLE_QUOTE, None))
                
            elif c == self.DOUBLE_QUOTE_SYMBOL:
                tokens.append(HTMLToken(HTMLTokenType.DOUBLE_QUOTE, None))
            
            elif c in self.whitespace:
                while c in self.whitespace:
                    curr_text += c
                    i += 1
                    c = html_text[i]
                tokens.append(HTMLToken(HTMLTokenType.WHITESPACE, len(curr_text)))
                curr_text = ""
                continue
                
            else:
                while not (c in self.ALL_SYMBOLS or c in self.whitespace):
                    curr_text += c
                    i += 1
                    c = html_text[i]
                tokens.append(HTMLToken(HTMLTokenType.STRING, curr_text))
                curr_text = ""
                continue
        
            i += 1
        
        return tokens
