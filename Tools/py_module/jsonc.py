'''
This module provides a function which loads a json file with c style comments.
'''
import json
import re

class JsonWithCommentsDecodeError(Exception):
    ''' This class represents the exception which can be happens in this module
    '''


def load(file):
    '''
    This functions loads a json file with c style comments
    Args:
        file: The json file object to be loaded
    '''

    try:
        # Read the json file text as string
        text = file.read()

        # Remove C language style comment /*.*\*/ and //.*
        text_without_comments = re.sub(r'/\*.*\*/|//.*', '', text)

        # Read result text and return the json object
        return json.loads(text_without_comments)

    except json.decoder.JSONDecodeError as json_ex:
        raise JsonWithCommentsDecodeError(json_ex.args[0]) from json_ex
    except Exception as ex:
        # Catch exceptions other than teh exceptions cached above
        raise ex

if __name__ == "__main__":
    # This is an example code

    with  open('./TestHarness/MakeConfig.json', 'r', encoding = 'UTF-8') as json_file:
        obj = load(json_file)
        print(obj)

    with  open('./TestCode/FifoBuffer/MakeConfig.json', 'r', encoding = 'UTF-8') as json_file:
        obj = load(json_file)
        print(obj)
