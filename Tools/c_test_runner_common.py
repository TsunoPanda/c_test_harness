''' This script provides the common parameters and APIs to c_test_runner.py and c_test_runner_gui.py
'''
import os
import glob
from typing import Final

TEST_CODE_CONFIG_FILE:Final[str]      = 'MakeConfig.jsonc'
TEST_HARNESS_CONFIG_FILE:Final[str]   = 'MakeConfig.jsonc'
DEFAULT_TEST_CODE_PATH:Final[str]     = '../Example/TestCode'
DEFAULT_TEST_HARNESS_PATH:Final[str]  = '../TestHarness'
DEFAULT_GLOBAL_CONFIG_PATH:Final[str] = '../GlobalMakeConfig.jsonc'

def get_all_module_under_folder(folder_path:str):
    """ This function returns the list of folders containing the file named TEST_CODE_CONFIG_FILE
    under the input folder.
    Args:
         folder_path: Folder path to be searched into.
    """
    module_list = glob.glob(f'{folder_path}/*/')
    module_list = [module for module in module_list
                          if os.path.exists(module + '/' + TEST_CODE_CONFIG_FILE)]
    module_list = list(map(lambda path: os.path.basename(path.rstrip('\\')),
                                module_list))
    return module_list
