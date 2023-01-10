''' This script provides the gui which runs c_test_runner.py.
'''
import os
import re
import tkinter
from tkinter import Tk, StringVar
from tkinter import filedialog
from tkinter import ttk
from tkinter import Listbox
from tkinter import Text
from tkinter.font import Font
import threading
from dataclasses import dataclass, field
from c_test_runner_common import get_all_module_under_folder
from c_test_runner_common import DEFAULT_TEST_CODE_PATH
from c_test_runner_common import DEFAULT_TEST_HARNESS_PATH
from c_test_runner_common import DEFAULT_GLOBAL_CONFIG_PATH

@dataclass
class RunTestParam:
    """ Input parameter of run_test_func of CTestRunnerGui
    """
    modules:list[str]          = field(default_factory = list) # List of modules to be tested
    run_type:str               = '' # clear or make or build
    global_config_path:str     = '' # Path to the global configuration file.
    test_directory:str         = '' # Path to the directory where test modules are located
    test_harness_directory:str = '' # Path to the directory where the test harness are located
    text_out                   = print # Function which output text string (e.g. print)

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
            # run_test_func is the function which runs the test.
            self.run_test_func           = run_func
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
            self.run_test_func(args[0])
        finally:
            self.__release_button_task()

    def __run_test_button_callback(self, run_type:str):
        if self.__acquire_button_task() is False:
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
                modules = [module for module in self.module_list.get(0, tkinter.END)
                            if module != 'All']
            else:
                modules = [module]

            test_directory         = self.test_module_dir_strvar.get()
            test_harness_directory = self.test_harness_dir_strvar.get()
            global_config_path     = self.grobal_config_file_strvar.get()
            self.textbox.delete("1.0","end")

            test_param = RunTestParam()
            test_param.modules = modules
            test_param.run_type = run_type
            test_param.global_config_path = global_config_path
            test_param.test_directory = test_directory
            test_param.test_harness_directory = test_harness_directory
            test_param.text_out = self.text_out

            thread = threading.Thread(
                target = self.__run_test,
                args   = (test_param,)
            )

            thread.start()
        except Exception as ex:
            print(ex.args[0])
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

                thread = threading.Thread(
                    target = self.__gen_covorage_report,
                    args=()
                    )
                thread.start()
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
            DEFAULT_TEST_CODE_PATH,
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
            DEFAULT_TEST_HARNESS_PATH,
            'Test Harness Directory: ',
            1
            )

        # global config file selection
        def callback_configuration_file_select_btn():
            this_dir = os.getcwd()
            open_dir = filedialog.askopenfilename(
                filetypes=[("global configuration file","*.jsonc")],
                initialdir=this_dir)
            if open_dir != "":
                self.grobal_config_file_strvar.set(open_dir)

        self.grobal_config_file_strvar = self.__set_dir_select_gui(
            directory_select_frame,
            self.grobal_config_file_strvar,
            callback_configuration_file_select_btn,
            DEFAULT_GLOBAL_CONFIG_PATH,
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
