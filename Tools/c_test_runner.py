''' This script runs the c code test.
'''
import os
import sys
import subprocess
from py_module.timestamp_comp import TimestampComp
from py_module.make import MakeFile, ExecutableStatus
from c_test_runner_gui import CTestRunnerGui
from c_test_runner_gui import RunTestParam
from c_test_runner_common import get_all_module_under_folder
from c_test_runner_common import TEST_CODE_CONFIG_FILE
from c_test_runner_common import TEST_HARNESS_CONFIG_FILE

def get_harness_config_path(harness_path) -> str:
    ''' This function returns the path to the configuration file of the test harness
    '''
    harness_config_path = f'{harness_path}/{TEST_HARNESS_CONFIG_FILE}'

    return harness_config_path

def get_the_test_config_path(test_module_path_in:str) -> str:
    ''' This function returns the path to the configuration file of
        the test module pointed by input directory path

    Args:
        test_module_in (str): The path to the directory which has the module to be tested
    '''
    # Make the local make configuration file path
    test_config_path = f'{test_module_path_in}/{TEST_CODE_CONFIG_FILE}'

    return test_config_path


def check_input_run_type(run_type_in:str) -> bool:
    ''' This function checks the validity of input run type.
        If it is not valid, stops this program with error message.

    Args:
        run_type_in (str): run type such as 'Make', 'Build', etc.
    '''

    # Is input run type valid?
    if run_type_in in ('Make', 'Build', 'Clear'):
        # Yes, input RunType is OK! return 'True'.
        return True

    # No, return 'False' with message
    print("Please input Make or Build or Clear as a second parameter.\n")
    print("If the second parameter is nothing, it will execute Make.\n")
    return False

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
                              run_type_in:str, string_out = print):
    '''This function executes the generate executable file
        according to the result of compilation.

    Args:
        in_target_path (str): Path to the executable object to be generated
        in_test_module (str): The module to be tested
        is_exe_valid (bool): True if the executable is ready
        run_type (str): 'Clear', 'Build', 'Make'
        log_file: Path to the log file where the result will be saved
    '''

    # The object files cleared?
    if run_type_in == 'Clear':
        # Then, it can't execute it. Just output message.
        string_out("\n***** Clear Done  *****\n\n")
    else:
        # object files has been not cleared.
        # Check the compilation finished without or with error.
        if is_exe_valid_in is True:
            # The valid executable file is exists, then execute it!
            string_out(f'\n***** Now execute {test_module_in} test code! *****\n\n')

            # Adding '2>&1' means send stderr(2) to the same place as stdout (&1))
            cmd = target_path.replace('/', '\\')

            # Display the command
            string_out(cmd)
            try:
                whole_msg_byte = subprocess.check_output(cmd,
                                                         stderr=subprocess.STDOUT,
                                                         shell=True)
                # Convert the binary into string
                whole_msg = whole_msg_byte.decode()
            except subprocess.CalledProcessError as error_process:
                whole_msg = error_process.output.decode()

            whole_msg_lines = whole_msg.splitlines()

            # Output result
            for line in whole_msg_lines:
                string_out(line)
        else:
            # The Compilation finished with error. Just output message.
            string_out('\n***** Some Errors detected...  *****\n\n')

def get_all_test_modules(test_code_base_path:str, test_module_in:str)->list[str]:
    """ This function returns all module to be tested as a list

    Args:
        test_code_base_path (str): Path to the folder which contains all test modules
        test_module (str): Name of the test module. if it is 'All' this function returns all test
                           module in the 'test_code_base_path'

    Returns:
        list[str]: list of module to be tested
    """

    # Clear the array of the test modules
    module_list_tmp = []

    if test_module_in == 'All':
        module_list_tmp = get_all_module_under_folder(test_code_base_path)
    else:
        module_list_tmp.append(test_module_in)

    return module_list_tmp

def get_command_line_arguments(test_code_base_path:str)->tuple[str, list[str], str]:
    """ This function analyzes command line arguments and returns input test module name,
        list of modules to be tested, and run type.

    Args:
        test_code_base_path (str): Path to the folder which contains modules to be tested

    Returns:
        tuple[str, list[str], str]: [input module name, modules to be tested, run type]
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
    """ This function makes module folder ready to be proceed test process.
        e.g. remove object files if one of them is older than the configuration file

    Args:
        make_obj (MakeFile): Make file object
        config_file_path (str): Path to the configuration file
    """
    objs = make_obj.load_json_makefile(config_file_path)
    objs_exists = [obj_file for obj_file in objs
                            if os.path.exists(obj_file)]
    if TimestampComp.is_the_file_oldest(config_file_path, objs_exists) is False:
        # Remove objs if config file is not oldest among object files
        for obj_exists in objs_exists:
            os.remove(obj_exists)

def run_test(run_test_param:RunTestParam):
    """ This function runs the test according to the input parameter which is defined in
    c_test_runner.gui.py.
    Args:
        run_test_param: The contents are defined in RunTestParam
    """
    if check_input_run_type(run_test_param.run_type) is False:
        return

    for test_module in run_test_param.modules:

        test_module_path = f'{run_test_param.test_directory}/{test_module}'

        # Make/Build/Clean Harness Codes
        make_file = MakeFile(string_out = run_test_param.text_out)

        make_file.load_json_makefile(run_test_param.global_config_path)

        prepare_module_block(make_file,
                             get_harness_config_path(run_test_param.test_harness_directory))

        prepare_module_block(make_file,
                             get_the_test_config_path(test_module_path))

        is_exe_valid = execute_makefile_process(make_file, run_test_param.run_type)

        execute_test_with_message(make_file.get_target_path(),
                                    test_module,
                                    is_exe_valid,
                                    run_test_param.run_type,
                                    string_out = run_test_param.text_out)

def generate_coveratge_report(out_path):
    """ This function invokes a command that generates a coverage reporting html files.
    Args:
         out_path: Path to the folder in which the generated files are going to be stored.
    """
    cmd = f"gcovr -r ../ --html-details --output={out_path}/coverage.html"
    subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)


if __name__ == "__main__":
    gui = CTestRunnerGui(run_test, generate_coveratge_report)
    gui.create_gui()
