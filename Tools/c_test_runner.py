''' This script runs the c code test.
'''
import os
import sys
import subprocess
import glob
import re
from typing import Final
import tkinter
from tkinter import Tk, StringVar
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkinter import Listbox
from tkinter import Text
from tkinter.font import Font
import threading
from py_module.timestamp_comp import TimestampComp
from py_module.make import MakeFile, ExecutableStatus

__TEST_CODE_CONFIG_FILE:Final[str]    = 'MakeConfig.jsonc'
__TEST_HARNESS_CONFIG_FILE:Final[str] = 'MakeConfig.jsonc'

def get_harness_config_path(harness_path) -> str:
    ''' This function returns the path to the configuration file of the test harness
    '''
    harness_config_path = f'{harness_path}/{__TEST_HARNESS_CONFIG_FILE}'

    return harness_config_path

def get_the_test_config_path(test_module_path_in:str) -> str:
    ''' This function returns the path to the configuration file of
        the test module pointed by input directory path

    Args:
        test_module_in (str): The path to the directory which has the module to be tested
    '''
    # Make the local make configuration file path
    test_config_path = f'{test_module_path_in}/{__TEST_CODE_CONFIG_FILE}'

    return test_config_path


def check_input_run_type(run_type_in:str) -> bool:
    ''' This function checks the validity of input run type.
        If it is not valid, stops this program with error message.

    Args:
        run_type_in (str): run type such as 'Make', 'Build', etc.
    '''

    # Is input run type valid?
    if run_type_in in ('Make', 'Build', 'Clear'):
        # Input RunType is OK! Do nothing.
        return True
    else:
        # No, exit with message
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

def get_all_module_under_folder(folder_path:str):
    module_list = glob.glob(f'{folder_path}/*/')
    module_list = [module for module in module_list
                          if os.path.exists(module + '/' + 'MakeConfig.jsonc')]
    module_list = list(map(lambda path: os.path.basename(path.rstrip('\\')),
                                module_list))
    return module_list

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

def run_test(test_module_list, run_type, global_make_config_file, code_path, harness_path, string_out = print):

    if check_input_run_type(run_type) == False:
        return

    for test_module in test_module_list:

        test_module_path = f'{code_path}/{test_module}'

        # Make/Build/Clean Harness Codes
        make_file = MakeFile(string_out = string_out)

        make_file.load_json_makefile(global_make_config_file)

        prepare_module_block(make_file, get_harness_config_path(harness_path))

        prepare_module_block(make_file, get_the_test_config_path(test_module_path))

        is_exe_valid = execute_makefile_process(make_file, run_type)

        execute_test_with_message(make_file.get_target_path(),
                                    test_module,
                                    is_exe_valid,
                                    run_type,
                                    string_out = string_out)

def generate_coveratge_report(out_path):
    cmd = f"gcovr -r ../ --html-details --output={out_path}/coverage.html"
    subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)

class CTestRunnerGui:
    def __init__(self, run_func, gen_func):
        self.tk_root                   = None
        self.test_module_dir_strvar    = None
        self.test_harness_dir_strvar   = None
        self.grobal_config_file_strvar = None
        self.module_list               = []
        self.textbox                   = None
        self.text_line_count             = 0
        if run_func is not None:
            self.run_test_func             = run_func
            # run_test_func is the function which runs the test.
            # Args:
            #       modules: List of modules to be tested
            #       run_type: clear or make or build
            #       global_config_path: Path to the global configuration file.
            #       test_directory: Path to the directory where test modules are located
            #       test_harness_directory: Path to the directory where the test harness are located
            #       text_out: Function which output text string (e.g. print)
        if gen_func is not None:
            self.gen_coverage_report_func = gen_func

        self.lock                = None
        self.clean_btn           = None
        self.make_btm            = None
        self.build_btm           = None
        self.gen_coverage_btn    = None
        self.coverage_report_dir = ""

    def text_out(self, text:str):
        lines = text.splitlines()
        for line_str in lines:
            self.text_line_count += 1
            current_line_count = self.text_line_count
            self.textbox.insert(tkinter.END, line_str+'\n')
            self.textbox.see(tkinter.END)

            # Font
            execution_match = re.match(r'\*+ Now execute .* test code\!', line_str)
            ok_match = re.match(r'^OK \(.*\)', line_str)
            ng_match = re.match(r'^Errors \(.*\)', line_str)
            if execution_match:
                self.textbox.tag_configure("bold", font=Font(size=12, weight="bold"))
                self.textbox.tag_add("bold",
                                     str(current_line_count)+'.0',
                                     str(current_line_count)+'.'+str(len(line_str)))
            elif ok_match:
                self.textbox.tag_configure("bold-and-blue",
                                           font=Font(size=12,weight="bold"),
                                           foreground='blue')
                self.textbox.tag_add("bold-and-blue",
                                     str(current_line_count)+'.0',
                                     str(current_line_count)+'.'+str(len(line_str)))
            elif ng_match:
                self.textbox.tag_configure("bold-and-red",
                                           font=Font(size=12, weight="bold"),
                                           foreground='red')
                self.textbox.tag_add("bold-and-red", str(current_line_count)+'.0',
                                     str(current_line_count)+'.'+str(len(line_str)))

    def set_run_test_function(self, func):
        self.run_test_func = func

    def update_module_list(self):
        test_module_dir = self.test_module_dir_strvar.get()
        self.module_list.delete(0, tkinter.END)
        for module_name in get_all_module_under_folder(test_module_dir):
            self.module_list.insert(tkinter.END, module_name)
        if self.module_list.size() != 0:
            self.module_list.insert(tkinter.END, 'All')

    def __acquire_button_task(self):
        if self.lock.acquire(blocking = False) is False:
            print('previous task may be working')
            return False

        self.clean_btn.configure(state = tkinter.DISABLED)
        self.make_btn.configure(state = tkinter.DISABLED)
        self.build_btn.configure(state = tkinter.DISABLED)
        self.gen_coverage_btn.configure(state = tkinter.DISABLED)
        return True

    def __release_button_task(self):
        self.lock.release()
        self.clean_btn.configure(state = tkinter.NORMAL)
        self.make_btn.configure(state = tkinter.NORMAL)
        self.build_btn.configure(state = tkinter.NORMAL)
        self.gen_coverage_btn.configure(state = tkinter.NORMAL)

    def __run_test(self, *args, **kwargs):
        try:
            self.run_test_func(*args, **kwargs)
        finally:
            self.__release_button_task()

    def __run_test_button_callback(self, run_type:str):
        if self.__acquire_button_task() == False:
            return

        try:
            if self.run_test_func is None:
                raise Exception

            self.text_line_count = 0

            selected_idx_list = self.module_list.curselection()
            if len(selected_idx_list) != 1:
                print('Please select one module to be tested')
                raise Exception
            selected_idx = selected_idx_list[0] # Assume only one item is selected
            module = self.module_list.get(selected_idx)
            if module == 'All':
                modules = [module for module in self.module_list.get(0, tkinter.END) if module != 'All']
            else:
                modules = [module]

                test_directory         = self.test_module_dir_strvar.get()
                test_harness_directory = self.test_harness_dir_strvar.get()
                global_config_path     = self.grobal_config_file_strvar.get()
                self.textbox.delete("1.0","end")
                th = threading.Thread(
                    target=self.__run_test,
                    args=(
                        modules,
                        run_type,
                        global_config_path,
                        test_directory,
                        test_harness_directory,
                        self.text_out
                        )
                    )

                th.start()
        except:
            self.__release_button_task()

    def __gen_covorage_report(self):
        try:
            self.gen_coverage_report_func(self.coverage_report_dir)
        finally:
            self.__release_button_task()

    def __gen_covorage_report_btn_callback(self):
        if self.__acquire_button_task() == False:
            return

        try:
            this_dir = os.getcwd()
            open_dir = filedialog.askdirectory(initialdir=this_dir)
            if open_dir != "":
                self.coverage_report_dir = open_dir

                th = threading.Thread(
                    target = self.__gen_covorage_report,
                    args=()
                    )
                th.start()
        except:
            self.__release_button_task()

    @staticmethod
    def __set_dir_select_gui(frame, str_var, callback, init_dir, label, row_in):
        str_var = StringVar()
        target_select_label = ttk.Label(frame, text = label)
        target_select_entry = ttk.Entry(frame, width = 100, textvariable=str_var)
        target_select_button = ttk.Button(
            frame, width = 5,
            text='...', command= callback
            )

        target_select_label.grid(row = row_in, column = 0, pady = (0, 8))
        target_select_entry.grid(row = row_in, column = 1, pady = (0, 8), sticky=tkinter.EW)
        target_select_button.grid(row = row_in, pady = (0, 8), column = 2)
        str_var.set(init_dir)

        return str_var

    def create_gui(self):
        self.lock = threading.Lock()
        self.tk_root = Tk()
        self.tk_root.title('C Test Runner')
        self.tk_root.grid_columnconfigure(0, weight=1)

        # Directory Selecting Frame
        directory_select_frame = ttk.Frame(self.tk_root)

        # test module selection
        def callback_test_module_select_btn():
            this_dir = os.getcwd()
            open_dir = filedialog.askdirectory(initialdir=this_dir)
            if open_dir != "":
                self.test_module_dir_strvar.set(open_dir)
            self.update_module_list()

        self.test_module_dir_strvar = self.__set_dir_select_gui(
            directory_select_frame,
            self.test_module_dir_strvar,
            callback_test_module_select_btn,
            '../Test/TestCode',
            'Test module directory: ',
            0
            )

        # test harness directory selection
        def callback_harness_dir_select_btn():
            this_dir = os.getcwd()
            open_dir = filedialog.askdirectory(initialdir=this_dir)
            if open_dir != "":
                self.test_harness_dir_strvar.set(open_dir)

        self.test_harness_dir_strvar = self.__set_dir_select_gui(
            directory_select_frame,
            self.test_harness_dir_strvar,
            callback_harness_dir_select_btn,
            '../Test/TestHarness',
            'Test Harness Directory: ',
            1
            )

        # global config file selection
        def callback_configuration_file_select_btn():
            this_dir = os.getcwd()
            open_dir = filedialog.askopenfilename(filetypes=[("global configuration file","*.jsonc")], initialdir=this_dir)
            if open_dir != "":
                self.grobal_config_file_strvar.set(open_dir)

        self.grobal_config_file_strvar = self.__set_dir_select_gui(
            directory_select_frame,
            self.grobal_config_file_strvar,
            callback_configuration_file_select_btn,
            '../Test/GlobalMakeConfig.jsonc',
            'Global configuration file: ',
            2
            )

        directory_select_frame.grid_columnconfigure(1, weight=1)
        directory_select_frame.grid(sticky=tkinter.EW, padx = 8, pady = (8, 0))

        # Module list and Message window frame
        module_list_text_frame = ttk.Frame(self.tk_root)

        v = StringVar(value = None)
        self.module_list = Listbox(module_list_text_frame, listvariable=v,
                 selectmode='browse', height=20)
        self.module_list.grid(row=0, column=0)
        self.update_module_list()

        scrollbar = ttk.Scrollbar(
            module_list_text_frame,
            orient=tkinter.VERTICAL,
            command=self.module_list.yview)
        self.module_list['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, sticky=(tkinter.N, tkinter.S))

        f = Font(family='arial', size = 10)
        v1 = StringVar()
        self.textbox = Text(module_list_text_frame, height=20, width=70)
        self.textbox.configure(font=f)
        self.textbox.grid(row=0, column=2, sticky=tkinter.EW)

        scrollbar = ttk.Scrollbar(
            module_list_text_frame,
            orient=tkinter.VERTICAL,
            command = self.textbox.yview)
        self.textbox['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=3, sticky=(tkinter.N, tkinter.S))
        module_list_text_frame.grid(row=1, sticky=tkinter.EW, padx = 8, pady = (8, 0))
        module_list_text_frame.grid_columnconfigure(2, weight=1)

        # Button frame
        buttons_frame = ttk.Frame(self.tk_root)
        self.clean_btn = ttk.Button(
            buttons_frame,
            text='Clear',
            command=lambda: self.__run_test_button_callback('Clear'))
        self.clean_btn.grid(row=0, column=0, sticky=tkinter.E)

        self.make_btn = ttk.Button(
            buttons_frame,
            text='Make',
            command=lambda: self.__run_test_button_callback('Make'))
        self.make_btn.grid(row=0, column=1, sticky=tkinter.E)

        self.build_btn = ttk.Button(
            buttons_frame,
            text='Build',
            command=lambda: self.__run_test_button_callback('Build'))
        self.build_btn.grid(row=0, column=2, sticky=tkinter.E)

        self.gen_coverage_btn = ttk.Button(
            buttons_frame,
            text='Generate Coverage Report',
            command= lambda: self.__gen_covorage_report_btn_callback())
        self.gen_coverage_btn.grid(row=0, column=3, sticky=tkinter.E)

        buttons_frame.grid(row=2, sticky=tkinter.E, padx = 8, pady = 8)
        self.tk_root.mainloop()

if __name__ == "__main__":
    gui = CTestRunnerGui(run_test, generate_coveratge_report)
    gui.create_gui()

