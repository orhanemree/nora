from urllib.request import urlopen
from json import loads
from os.path import abspath
from .tokenizer import CSSTokenizer


SRC_REPO = "romainmenke/css-tokenizer-tests"
SRC_URL  = f"https://api.github.com/repos/{SRC_REPO}/git/trees/main?recursive=1"
TEST_BASE_URL = f"https://raw.githubusercontent.com/{SRC_REPO}/main/tests"


def camel2snake(camel: str) -> str:
    
    """
    Convert camelCase into snake_case. Also convert "-"s into "_"s.
    
    camel:\n\r String to be converted.
    """
    
    snake = ""
        
    for c in camel:
        
        if c.isupper():
            snake += "_"
            snake += c.lower()
        
        elif c == "-":
            snake += "_"
        
        else: snake += c
    
    return snake


def list_test_names(out_file: str = None) -> None | list[str]:
    
    """
    List all tests for tokenizer in SRC_REPO with GitHub API. Write test names into the out_file if is provided.
    Return test names as a list.
    
    out_file:\n\t Path to output file.
    """    
    
    # open github repo
    res = urlopen(SRC_URL)

    # get repo tree
    tree = loads(res.read())["tree"]
    
    # fins source.css files in the repo and get names
    start_i = "tests/"
    end_i   = "/source.css"
    names = [t["path"][len(start_i):-len(end_i)] for t in tree if t["path"].startswith(start_i) and t["path"].endswith(end_i)]
    
    if out_file is not None:
        with open(abspath(out_file), "w") as f:
            f.writelines(name + "\n" for name in names)
    
    return names


def _test_check_properties(tok_expected: dict, tok_output: dict):
    
    for p in tok_expected["structured"] or []:
        val_expected = tok_expected["structured"][p]
        val_output = getattr(tok_output, camel2snake(p))
    
        if val_expected != val_output:
            return False
    
    return True


def run_test(test_name: str | list[str], out_file: str = None) -> None | list[str]:
    
    """
    Run a single test or list of tests of tokenizer from the list. Write failed test names into the out_file
    if is provided. Return failed test names as a list.
    
    test_name:\n\t Test or tests to run.
    out_file:\n\t Path to output file.
    """
    
    if type(test_name) == str:
        test_name = [test_name]
        
    # initialize tokenizer
    tokneizer = CSSTokenizer()
        
    source_end = "source.css"
    tokens_end = "tokens.json"
        
    total_success = 0
    total_fail = 0
    failed_list = []
    
    for name in test_name:
        
        # get source.css and tokens.json files from the repo with GitHub API
        source = urlopen(f"{TEST_BASE_URL}/{name}/{source_end}").read().decode("utf-8")
        tokens = loads(urlopen(f"{TEST_BASE_URL}/{name}/{tokens_end}").read().decode("utf-8"))
        tokens.append({"type": "eof-token", "structured": None})
        
        # run css tokenizer
        out = tokneizer.run(source)
        curr_tok = 0
        while 1: 
            
            try:
                tok_output   = next(out)
                tok_expected = tokens[curr_tok]
            
                # check token type
                type_exp = tok_expected["type"].replace("-token", "")\
                    .replace("[", "left-square")\
                    .replace("]", "right-square")\
                    .replace("(", "left-paren")\
                    .replace(")", "right-paren")\
                    .replace("{", "left-brace")\
                    .replace("}", "right-brace")
                type_out = tok_output.tok_type.name
                
                # comment token is ignored int the tokenizer, so ingore it here too
                if type_exp == "comment":
                    continue
                
                if type_exp not in ("CDC", "CDO"):
                    # make json token compatible with this this lib's API
                    type_exp = type_exp.replace("-token", "").replace("-", "_")
                    type_out = type_out.lower()
                
                if type_exp != type_out:
                    print(f"🔴 FAIL: {name}, e: token type mismatch")
                    total_fail += 1
                    failed_list.append(name)
                    break
            
                # check token properties
                ret = _test_check_properties(tok_expected, tok_output)
                if ret == 0:
                    print(f"🔴 FAIL: {name}, e: token property mismatch")
                    total_fail += 1
                    failed_list.append(name)
                    break
                
            except StopIteration:
                print(f"🟢 SUCCESS: {name}")
                total_success += 1
                break
        
            except Exception as e:
                print(f"🔴 FAIL: {name}, e: {e}")
                total_fail += 1
                failed_list.append(name)
                break
                
            curr_tok += 1
    
    print("Total success:", total_success)
    print("Total fail:", total_fail)
    
    if out_file is not None:
        with open(abspath(out_file), "w") as f:
            f.writelines(failed_name + "\n" for failed_name in failed_list)
            
    return failed_list
