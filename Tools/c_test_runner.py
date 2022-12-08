''' This script runs the c code test.
'''
import os
import sys
import subprocess
import glob
from typing import List, Tuple
from py_module.timestamp_comp import TimestampComp
from py_module.make import MakeFile, ExecutableStatus

__TEST_BASE_PATH           = '../Test'
__TEST_CODE_PATH           = __TEST_BASE_PATH+'/TestCode'
__TEST_HARNESS_PATH        = __TEST_BASE_PATH+'/TestHarness'
__TEST_CODE_CONFIG_FILE    = 'MakeConfig.jsonc'
__TEST_HARNESS_CONFIG_FILE = 'MakeConfig.jsonc'
__TEST_LOG_DIR             = __TEST_BASE_PATH+'/Log'

def check_file_dir_existance(dir_path:str):
    ''' This function shut down this script if the directory
    pointed by the input path does not exist.

    Args:
        dir_path (str): The directory path to be checked
    '''

    if not os.path.exists(dir_path):
        # It did not exist.
        print(f'Could not find the {dir_path}')
        sys.exit(1)

def get_harness_config_path() -> str:
    ''' This function returns the path to the configuration file of the test harness
    '''
    harness_config_path = f'{__TEST_HARNESS_PATH}/{__TEST_HARNESS_CONFIG_FILE}'

    check_file_dir_existance(harness_config_path)

    return harness_config_path

def get_the_test_config_path(test_module_in:str) -> str:
    ''' This function returns the path to the configuration file of
        the test module pointed by input directory path

    Args:
        test_module_in (str): The path to the directory which has the module to be tested
    '''
    # Make the local make configuration file path
    test_config_path = f'{__TEST_CODE_PATH}/{test_module_in}/{__TEST_CODE_CONFIG_FILE}'

    check_file_dir_existance(test_config_path)

    return test_config_path


def check_input_run_type(run_type_in:str):
    ''' This function checks the validity of input run type.
        If it is not valid, stops this program with error message.

    Args:
        run_type_in (str): run type such as 'Make', 'Build', etc.
    '''

    # Is input run type valid?
    if run_type_in in ('Make', 'Build', 'Clear'):
        # Input RunType is OK! Do nothing.
        pass
    else:
        # No, exit with message
        print("Please input Make or Build or Clear as a second parameter.\n")
        print("If the second parameter is nothing, it will execute Make.\n")
        sys.exit(1)

def execute_makefile_process(in_make_file:MakeFile, run_type_in:str):
    ''' This function executes make process according to the input run type.
        And return the compile state and clear state.
    '''

    is_exe_valid_tmp = False

    # Check the input run type
    if run_type_in == 'Make':
        # The run type is 'Make'
        # Call Make function and save the status
        is_exe_valid_tmp = (in_make_file.make() == ExecutableStatus.EXECUTABLE_VALID)

    elif run_type_in == 'Build':
        # The run type is 'Build'
        # Call Build function and save the status
        is_exe_valid_tmp = (in_make_file.build() == ExecutableStatus.EXECUTABLE_VALID)

    elif run_type_in == 'Clear':
        # The run type is 'Clear'
        # Call Clear function
        in_make_file.clear()

    # Returns the status
    return is_exe_valid_tmp

def execute_test_with_message(target_path:str, test_module_in:str, is_exe_valid_in:bool,
                              run_type_in:str, log_file_in):
    """This function executes the generate executable file
        according to the result of compilation.

    Args:
        in_target_path (str): _description_
        in_test_module (str): The module to be tested
        is_exe_valid (bool): _description_
        run_type (str): _description_
        log_file (_type_): _description_
    """

    # The object files cleared?
    if run_type_in == 'Clear':
        # Then, it can't execute it. Just output message.
        print("\n***** Clear Done  *****\n\n")
    else:
        # object files has been not cleared.
        # Check the compilation finished without or with error.
        if is_exe_valid_in is True:
            # The valid executable file is exists, then execute it!
            print(f'\n***** Now execute {test_module_in} test code! *****\n\n')

            # Adding '2>&1' means send stderr(2) to the same place as stdout (&1))
            cmd = target_path.replace('/', '\\')

            # Display the command
            print(cmd)
            try:
                whole_msg_byte = subprocess.check_output(cmd,
                                                         stderr=subprocess.STDOUT,
                                                         shell=True)
                # Convert the binary into string
                whole_msg = whole_msg_byte.decode()
            except subprocess.CalledProcessError as error_process:
                whole_msg = error_process.output.decode()


            whole_msg_lines = whole_msg.splitlines()

            # Output the results to the log file
            count_astarisks_in_test_message = 90
            test_message = test_module_in + " Test Result"
            astarisks = '*' * int(count_astarisks_in_test_message)
            astarisks_left = '*' * int(((count_astarisks_in_test_message-2-len(test_message))/2))

            astarisks_right = (      astarisks_left       if ((len(test_message) % 2) == 0)
                                else astarisks_left + '*' )
            log_file_in.write(astarisks + '\n')
            log_file_in.write(astarisks_left + ' ' + test_message + ' ' + astarisks_right + '\n')
            log_file_in.write(astarisks + '\n\n')
            log_file_in.write('\n'.join(whole_msg_lines))
            log_file_in.write(test_message + ' END\n\n\n')

            # Output result to STDOUT
            print(whole_msg)
        else:
            # The Compilation finished with error. Just output message.
            print('\n***** Some Errors detected...  *****\n\n')

def get_all_test_modules(test_code_base_path:str, test_module_in:str)->List[str]:
    """_summary_

    Args:
        test_code_base_path (str): _description_
        test_module (str): _description_

    Returns:
        List[str]: list of module to be tested
    """

    # Clear the array of the test modules
    module_list_tmp = []

    if test_module_in == 'All':
        module_list_tmp = glob.glob(f'{test_code_base_path}/*/')
        module_list_tmp = list(map(lambda path: os.path.basename(path.rstrip('\\')),
                                   module_list_tmp))
    else:
        module_list_tmp.append(test_module_in)

    return module_list_tmp

def get_command_line_arguments(test_code_base_path:str)->Tuple[str, List[str], str]:
    """_summary_

    Args:
        test_code_base_path (str): _description_

    Returns:
        Tuple[str, List[str], str]: _description_
    """
    # Check the number of input command line arguments.
    if len(sys.argv) < 2:
        # No arguments. Then, exit with messages
        print("Please input the test module as the first parameter.\n")
        sys.exit(1)
    else:
        # Two arguments.
        # Get test module name from the first parameter.
        test_module_tmp = sys.argv[1]
        module_list_tmp = get_all_test_modules(test_code_base_path, test_module_tmp)

        if len(sys.argv) < 3:
            # Assume the second parameter is 'Make'
            run_type_tmp    = 'Make'
        else:
            # Get run type from the second parameter.
            run_type_tmp    = sys.argv[2]

    return (test_module_tmp, module_list_tmp, run_type_tmp)

def prepare_module_block(make_obj:MakeFile, config_file_path:str):
    """_summary_

    Args:
        make_obj (MakeFile): _description_
        config_file_path (str): _description_
    """
    objs = make_obj.load_json_makefile(config_file_path)
    objs_exists = [obj_file for obj_file in objs
                            if os.path.exists(obj_file)]
    if TimestampComp.is_the_file_oldest(config_file_path, objs_exists) is False:
        # Remove objs if config file is not oldest among object files
        for obj_exists in objs_exists:
            os.remove(obj_exists)

# main code
if __name__ == "__main__":
    input_var = get_command_line_arguments(__TEST_CODE_PATH)
    test_module_or_all, module_list, run_type = input_var
    if not os.path.exists(__TEST_BASE_PATH):
        sys.exit("The test folder doesn't exist")

    if not os.path.exists(__TEST_LOG_DIR):
        os.mkdir(__TEST_LOG_DIR)

    with  open(f'{__TEST_LOG_DIR}/{test_module_or_all}.txt', 'w', encoding = 'UTF-8') as log_file:

        for test_module in module_list:

            check_input_run_type(run_type)

            test_module_path = f'{__TEST_CODE_PATH}/{test_module}'
            check_file_dir_existance(test_module_path)

            # Make/Build/Clean Harness Codes
            make_file = MakeFile()

            make_file.load_json_makefile(__TEST_BASE_PATH+'/GlobalMakeConfig.jsonc')

            prepare_module_block(make_file, get_harness_config_path())

            prepare_module_block(make_file, get_the_test_config_path(test_module))

            is_exe_valid = execute_makefile_process(make_file, run_type)

            execute_test_with_message(make_file.get_target_path(),
                                      test_module,
                                      is_exe_valid,
                                      run_type,
                                      log_file)
