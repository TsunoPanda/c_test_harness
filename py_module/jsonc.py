'''
This module provides a function which loads a json file with c style comments.
'''
import json
import re

def load(file):
    '''
    This functions loads a json file with c style comments
    file: json file object
    '''
    # Read the json file text as string
    text = file.read()

    # Remove C language style comment /*.*\*/ and //.*
    text_without_comments = re.sub(r'/\*.*\*/|//.*', '', text)

    # Read result text and return the json object
    return json.loads(text_without_comments)

if __name__ == "__main__":
    with  open('./TestHarness/MakeConfig.json', 'r', encoding = 'UTF-8') as json_file:
        obj = load(json_file)
        print(obj)

    with  open('./TestCode/FifoBuffer/MakeConfig.json', 'r', encoding = 'UTF-8') as json_file:
        obj = load(json_file)
        print(obj)
