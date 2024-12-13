from urllib.request import urlopen
from json import loads

from .tokenizer import *


def camel2snake(camel: str):
    
    snake = ""
        
    for c in camel:
        
        if c.isupper():
            snake += "_"
            snake += c.lower()
        
        elif c == "-":
            snake += "_"
        
        else: snake += c
    
    return snake


SRC_REPO = "romainmenke/css-tokenizer-tests"
SRC_URL  = f"https://api.github.com/repos/{SRC_REPO}/git/trees/main?recursive=1"

TEST_BASE_URL = f"https://raw.githubusercontent.com/{SRC_REPO}/main/tests"


def main():
    # open github repo
    res = urlopen(SRC_URL)
    
    # list source.css and tokens.json files
    tree = loads(res.read())["tree"]
    sources = [t["path"].replace("tests/", "") for t in tree if t["path"].startswith("tests/") and t["path"].endswith("source.css")]
    tokenss = [t["path"].replace("tests/", "") for t in tree if t["path"].startswith("tests/") and t["path"].endswith("tokens.json")]


    # initialize tokenizer
    tokenizer = CSSTokenizer()
    
    total_success = 0
    total_fail = 0
    fails = []
    
    for i in range(len(sources)):
        
        # read source.css and tokens.json files
        source = urlopen(f"{TEST_BASE_URL}/{sources[i]}").read().decode("utf-8")
        tokens = loads(urlopen(f"{TEST_BASE_URL}/{tokenss[i]}").read().decode("utf-8"))
        tokens.append({"type": "eof-token", "structured": None})
    
        # run tokenizer
        output = tokenizer.run(source)
    
        # get all tokens
        n = 0
        failed = 0
        while not failed:
            test_name = f"src: {sources[i]}"
            try: 
                
                tok_output = next(output)
                tok_expected = tokens[n]
                
                # check token type
                if camel2snake(tok_expected["type"]) != tok_output.tok_type.name.lower()+"_token":
                    print(f"🔴 FAIL: {test_name}")
                    total_fail += 1
                    fails.append(test_name)
                    failed = 1
                
                # check token properties
                for p in tok_expected["structured"] or []:
                    val_expected = tok_expected["structured"][p]
                    val_output = getattr(tok_output, camel2snake(p))
                    
                    if val_expected != val_output:
                        print(f"🔴 FAIL: {test_name}")
                        total_fail += 1
                        fails.append(test_name)
                        failed = 1
            
            except StopIteration:
                print(f"🟢 SUCCESS: {test_name}")
                total_success += 1
                break
        
            except Exception as e:
                print(f"🔴 FAIL: {test_name}, e: {e}")
                total_fail += 1
                fails.append(test_name)
                failed = 1
            
            n += 1

    print("Total success:", total_success)
    print("Total fail:", total_fail)
    print("Fails:", fails)
