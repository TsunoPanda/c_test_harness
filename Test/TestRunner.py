import os
import sys
import subprocess
import glob
from enum import Enum
from typing import List
import jsonc
import TimeStampComp
from Makefile import MakeFile, ExecutableStatus

__TEST_CODE_PATH           = './TestCode'
__TEST_HARNESS_PATH        = './TestHarness'
__TEST_CODE_CONFIG_FILE    = 'MakeConfig.jsonc'
__TEST_HARNESS_CONFIG_FILE = 'MakeConfig.jsonc'

def CheckFileDirExsitance(file_path):
    # The configuration file exist?
    if not os.path.exists(file_path):
        # It did not exist.
        print(f'Could not find the {file_path}')
        exit(1)

def GetHarnessConfigPath():
    # Make the global make configuration file path
    harnessConfigPath = f'./{__TEST_HARNESS_PATH}/{__TEST_HARNESS_CONFIG_FILE}'

    CheckFileDirExsitance(harnessConfigPath)

    return(harnessConfigPath)

def GetTheTestConfigPath(TestModule):

    # Make the local make configuration file path
    testConfigPath = f'./{__TEST_CODE_PATH}/{TestModule}/{__TEST_CODE_CONFIG_FILE}'

    CheckFileDirExsitance(testConfigPath)

    return(testConfigPath)


def CheckInputRunType(RunType):
    ''' This function checks the validity of input run type.
        If it is not valid, stops this program with error message.
    '''

    # Is input run type valid?
    if (
        RunType == 'Make'  or
        RunType == 'Build' or
        RunType == 'Clear'
        ):
        # Input RunType is OK! Do nothing.
        pass
    else:
        # No, exit with message
        print("Please input Make or Build or Clear as a second parameter.\n");
        print("If the second parameter is nothing, it will execute Make.\n");
        exit(1);

def ExecMakeFileProcess(make_file, RunType):
    ''' This function executes make process according to the input run type.
        And return the compile state and clear state.
     '''

    # Check the input run type
    if RunType == 'Make':
        # The run type is 'Make'
        # Call Make function and save the status
        isExeValid = (make_file.Make() == ExecutableStatus.EXECUTABLE_VALID)

    elif RunType == 'Build':
        # The run type is 'Build'
        # Call Build function and save the status
        isExeValid = (make_file.Build() == ExecutableStatus.EXECUTABLE_VALID)

    elif RunType == 'Clear':
        # The run type is 'Clear'
        # Call Clear function
        make_file.Clear()

        isExeValid = False

    # Returns the status
    return isExeValid

def ExecuteTestWithMessage(target_path, TestModule, isExeValid, RunType, LOG_FILE):
    ''' This function executes the generate executable file
        according to the result of compilation.
        $TestModule: The module to be tested
        $IsNoCompileError: Compilation result
        $IsCleared: Has object files cleared or not
    '''

    # The object files cleared?
    if RunType == 'Clear':
        # Then, it can't execute it. Just output message.
        print("\n***** Clear Done  *****\n\n")
    else:
        # object files has been not cleared.
        # Check the compilation finished without or with error.
        if isExeValid == True:
            # The valid executable file is exists, then execute it!
            print(f'\n***** Now execute {TestModule} test code! *****\n\n')

            # Adding '2>&1' means send stderr(2) to the same place as stdout (&1))
            cmd = target_path + ' -v 2>&1'
            cmd = cmd.replace('/', '\\')

            # Display the command
            print(cmd);
            try:
                whole_msg_byte = subprocess.check_output(cmd,
                                                         stderr=subprocess.STDOUT,
                                                         shell=True)
                # Convert the binary into string
                whole_msg = whole_msg_byte.decode()
            except subprocess.CalledProcessError as e:
                whole_msg = e.output.decode()


            whole_msg_lines = whole_msg.splitlines()

            # Output the results to the log file
            TestMessageNumOfAstarisks = 90
            TestMessage = TestModule + " Test Result"
            astarisks = '*' * int(TestMessageNumOfAstarisks)
            astarisks_left = '*' * int(((TestMessageNumOfAstarisks-2-len(TestMessage))/2))
                
            astarisks_right = (      astarisks_left       if ((len(TestMessage) % 2) == 0)
                                else astarisks_left + '*' )
            LOG_FILE.write(astarisks + '\n')
            LOG_FILE.write(astarisks_left + ' ' + TestMessage + ' ' + astarisks_right + '\n')
            LOG_FILE.write(astarisks + '\n\n')
            LOG_FILE.write('\n'.join(whole_msg_lines))
            LOG_FILE.write(TestMessage + ' END\n\n\n')

            # Output result to STDOUT
            print(whole_msg)
        else:
            # The Compilation finished with error. Just output message.
            print('\n***** Some Errors detected...  *****\n\n')

def GetAllTestModules(test_code_base_path, TestModule):
    # Clear the array of the test modules
    aTestModule_ref = []

    if TestModule == 'All':
        aTestModule_ref = glob.glob(f'{test_code_base_path}/*/')
        aTestModule_ref = list(map(lambda path: os.path.basename(path.rstrip('\\')), aTestModule_ref))
    else:
        aTestModule_ref.append(TestModule)

    return aTestModule_ref

def GetCommandLineArguments(test_code_base_path):
    # Check the number of input command line arguments.
    if len(sys.argv) < 2:
        # No arguments. Then, exit with messages
        print("Please input the test module as the first parameter.\n");
        exit(1)
    else:
        # Two arguments.
        # Get test module name from the first parameter.
        TestModule = sys.argv[1]
        aTestModule_ref = GetAllTestModules(test_code_base_path, TestModule)

        if len(sys.argv) < 3:
            # Assume the second parameter is 'Make'
            RunType    = 'Make'
        else:
            # Get run type from the second parameter.
            RunType    = sys.argv[2]

    return(TestModule, aTestModule_ref, RunType)

def prepare_module_block(make_obj, config_file_path):
    objs = make_obj.load_json_makefile(config_file_path)
    objs_exists = [obj_file for obj_file in objs
                            if os.path.exists(obj_file)]
    if TimeStampComp.IsTheFileOldest(config_file_path, objs_exists) == False:
        # Remove objs if config file is not oldest among object files
        for obj_exists in objs_exists:
            os.remove(obj_exists)

# main code
if __name__ == "__main__":
    TestModuleOrAll, aTestModule_ref, RunType = GetCommandLineArguments(__TEST_CODE_PATH)

    with  open(f'TestLog_{TestModuleOrAll}.txt', 'w', encoding = 'UTF-8') as LOG_FILE:

        for TestModule in aTestModule_ref:

            CheckInputRunType(RunType)

            test_module_path = f'{__TEST_CODE_PATH}/{TestModule}'
            CheckFileDirExsitance(test_module_path)

            # Make/Build/Clean Harness Codes
            make_file = MakeFile()

            make_file.load_json_makefile('./GlobalMakeConfig.jsonc')

            prepare_module_block(make_file, GetHarnessConfigPath())

            prepare_module_block(make_file, GetTheTestConfigPath(TestModule))

            isExeValid = ExecMakeFileProcess(make_file, RunType)

            ExecuteTestWithMessage(make_file.get_target_path(), TestModule, isExeValid, RunType, LOG_FILE)


