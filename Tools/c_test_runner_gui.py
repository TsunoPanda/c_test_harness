""" This script provides the gui which runs c_test_runner.py.
"""
from __future__ import annotations
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
from py_module.tk_button import MultiTaskButton

@dataclass
class RunTestParam: # TODO: will move to common
    """ Input parameter of run_test_func of CTestRunnerGui
    """
    modules:list[str]          = field(default_factory = list) # List of modules to be tested
    run_type:str               = '' # clear or make or build
    global_config_path:str     = '' # Path to the global configuration file.
    test_directory:str         = '' # Path to the directory where test modules are located
    test_harness_directory:str = '' # Path to the directory where the test harness are located
    text_out                   = print # Function which output text string (e.g. print)

class DirectorySelectingFrame:
    """ This class indicates a GUI frame including "test module directory selector",
        "test harness directory selector", and "global configuration file selector".
    """
    def __init__(self, tk_root):
        self.tk_root                   = tk_root
        self.frame                     = ttk.Frame(self.tk_root)
        self.test_module_dir_strvar    = None
        self.test_harness_dir_strvar   = None
        self.global_config_file_strvar = None
        self.update_end_hook           = None

    def __set_dir_select_gui(self, callback, init_dir, label, row_in):
        str_var = StringVar()
        target_select_label = ttk.Label(self.frame, text = label)
        target_select_entry = ttk.Entry(self.frame, width = 100, textvariable=str_var)
        target_select_button = ttk.Button(
            self.frame, width = 5,
            text='...', command= callback
            )

        target_select_label.grid(row = row_in, column = 0, pady = (0, 8))
        target_select_entry.grid(row = row_in, column = 1, pady = (0, 8), sticky=tkinter.EW)
        target_select_button.grid(row = row_in, pady = (0, 8), column = 2)
        str_var.set(init_dir)

        return str_var

    def get_test_module_dir(self):
        """ This method returns the directory path to the module to be tested
        """
        return self.test_module_dir_strvar.get()

    def get_test_harness_dir(self):
        """ This method returns the directory path to the test harness codes
        """
        return self.test_harness_dir_strvar.get()

    def get_global_config_file_path(self):
        """ This method returns the path to the global configuration file
        """
        return self.global_config_file_strvar.get()

    def set_test_module_dir(self, path):
        """ This method sets the directory path to the module to be tested
        """
        self.test_module_dir_strvar.set(path)

    def set_test_harness_dir(self, path):
        """ This method sets the directory path to test harness codes
        """
        self.test_harness_dir_strvar.set(path)

    def set_global_config_file_path(self, path):
        """ This method sets the path to the global configuration file
        """
        self.global_config_file_strvar.set(path)

    def set_update_end_hook(self, callback):
        """ This method set the function that will be called when on of the directory or file
            path was changed.
        """
        self.update_end_hook = callback

    # test module selection
    def __callback_test_module_select_btn(self):
        this_dir = os.getcwd()
        open_dir = filedialog.askdirectory(initialdir=this_dir)
        if open_dir != "":
            self.set_test_module_dir(open_dir)

            if self.update_end_hook is not None:
                self.update_end_hook()

    # test harness directory selection
    def __callback_harness_dir_select_btn(self):
        this_dir = os.getcwd()
        open_dir = filedialog.askdirectory(initialdir=this_dir)
        if open_dir != "":
            self.set_test_harness_dir(open_dir)

            if self.update_end_hook is not None:
                self.update_end_hook()

    # global config file selection
    def __callback_global_config_file_select_btn(self):
        this_dir = os.getcwd()
        open_dir = filedialog.askopenfilename(
            filetypes=[("global configuration file","*.jsonc")],
            initialdir=this_dir)
        if open_dir != "":
            self.global_config_file_strvar.set(open_dir)

            if self.update_end_hook is not None:
                self.update_end_hook()

    def create(self):
        # test module path selection
        self.test_module_dir_strvar = self.__set_dir_select_gui(
            self.__callback_test_module_select_btn,
            DEFAULT_TEST_CODE_PATH,
            'Test module directory: ',
            0
            )

        # test harness path selection
        self.test_harness_dir_strvar = self.__set_dir_select_gui(
            self.__callback_harness_dir_select_btn,
            DEFAULT_TEST_HARNESS_PATH,
            'Test Harness Directory: ',
            1
            )

        # test global config path selection
        self.global_config_file_strvar = self.__set_dir_select_gui(
            self.__callback_global_config_file_select_btn,
            DEFAULT_GLOBAL_CONFIG_PATH,
            'Global configuration file: ',
            2
            )

        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid(sticky=tkinter.EW, padx = 8, pady = (8, 0))

class ModuleListAndMessageFrame:
    """ This class indicates a GUI frame including "module list box" and "message box"
    """
    def __init__(self, tk_root):
        self.tk_root                   = tk_root
        self.frame                     = ttk.Frame(self.tk_root)
        self.module_list               = None
        self.textbox                   = None
        self.text_line_count             = 0

    def get_module_list(self):
        selected_idx_list = self.module_list.curselection()
        if len(selected_idx_list) != 1:
            raise ValueError('Please select one module to be tested')
        selected_idx = selected_idx_list[0] # Assume only one item is selected
        module = self.module_list.get(selected_idx)
        if module == 'All':
            modules = [module for module in self.module_list.get(0, tkinter.END)
                        if module != 'All']
        else:
            modules = [module]

        return modules

    def clear_text(self):
        # clear text
        self.textbox.delete("1.0", "end")
        # reset text_ line count
        self.text_line_count = 0

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

    def update_module_list(self, test_module_dir):
        self.module_list.delete(0, tkinter.END)
        for module_name in get_all_module_under_folder(test_module_dir):
            self.module_list.insert(tkinter.END, module_name)
        if self.module_list.size() != 0:
            self.module_list.insert(tkinter.END, 'All')

    def create(self):
        v = StringVar(value = None)
        self.module_list = Listbox(self.frame, listvariable=v,
                 selectmode='browse', height=20)
        self.module_list.grid(row=0, column=0)

        scrollbar = ttk.Scrollbar(
            self.frame,
            orient=tkinter.VERTICAL,
            command=self.module_list.yview)
        self.module_list['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, sticky=(tkinter.N, tkinter.S))

        f = Font(family='arial', size = 10)
        v1 = StringVar()
        self.textbox = Text(self.frame, height=20, width=70)
        self.textbox.configure(font=f)
        self.textbox.grid(row=0, column=2, sticky=tkinter.EW)

        scrollbar = ttk.Scrollbar(
            self.frame,
            orient=tkinter.VERTICAL,
            command = self.textbox.yview)
        self.textbox['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=3, sticky=(tkinter.N, tkinter.S))
        self.frame.grid(row=1, sticky=tkinter.EW, padx = 8, pady = (8, 0))
        self.frame.grid_columnconfigure(2, weight=1)

class TestButtonFrame:
    def __init__(self, tk_root):
        self.frame               = ttk.Frame(tk_root)
        self.lock                = threading.Lock()

        # run_test_func is the function which runs the test.
        self.clear_btn:MultiTaskButton           = None
        self.make_btn:MultiTaskButton            = None
        self.build_btn:MultiTaskButton           = None
        self.gen_coverage_btn:MultiTaskButton    = None
        self.test_start_hook                     = None

    def set_test_start_hook(self, hook):
        self.test_start_hook = hook

    def __test_start_hook(self):
        if self.lock.acquire(blocking = False) is False:
            raise LockAcquireFailError('The previous task is working')
        self.clear_btn.configure(state = tkinter.DISABLED)
        self.make_btn.configure(state = tkinter.DISABLED)
        self.build_btn.configure(state = tkinter.DISABLED)
        self.gen_coverage_btn.configure(state = tkinter.DISABLED)

        if self.test_start_hook is not None:
            self.test_start_hook()

    def __gen_start_hook(self):
        if self.lock.acquire(blocking = False) is False:
            raise LockAcquireFailError('The previous task is working')
        self.clear_btn.configure(state = tkinter.DISABLED)
        self.make_btn.configure(state = tkinter.DISABLED)
        self.build_btn.configure(state = tkinter.DISABLED)
        self.gen_coverage_btn.configure(state = tkinter.DISABLED)

    def __end_hook(self):
        self.lock.release()
        self.clear_btn.configure(state = tkinter.NORMAL)
        self.make_btn.configure(state = tkinter.NORMAL)
        self.build_btn.configure(state = tkinter.NORMAL)
        self.gen_coverage_btn.configure(state = tkinter.NORMAL)

    def create(self, clear_func, make_func, build_func, gen_func):
        self.clear_btn = MultiTaskButton(
            self.frame,
            text='Clear',
            task=clear_func)

        self.make_btn = MultiTaskButton(
            self.frame,
            text='Make',
            task= make_func )

        self.build_btn = MultiTaskButton(
            self.frame,
            text='Build',
            task= build_func)

        self.gen_coverage_btn = MultiTaskButton(
            self.frame,
            text='Generate Coverage Report',
            task= gen_func )

        self.clear_btn.set_task_start_hook(self.__test_start_hook)
        self.clear_btn.set_task_end_hook(self.__end_hook)
        self.clear_btn.set_exception_hook(self.__end_hook)

        self.make_btn.set_task_start_hook(self.__test_start_hook)
        self.make_btn.set_task_end_hook(self.__end_hook)
        self.make_btn.set_exception_hook(self.__end_hook)

        self.build_btn.set_task_start_hook(self.__test_start_hook)
        self.build_btn.set_task_end_hook(self.__end_hook)
        self.build_btn.set_exception_hook(self.__end_hook)

        self.gen_coverage_btn.set_task_start_hook(self.__gen_start_hook)
        self.gen_coverage_btn.set_task_end_hook(self.__end_hook)
        self.gen_coverage_btn.set_exception_hook(self.__end_hook)

        self.clear_btn.grid(row=0, column=0, sticky=tkinter.E)
        self.make_btn.grid(row=0, column=1, sticky=tkinter.E)
        self.build_btn.grid(row=0, column=2, sticky=tkinter.E)
        self.gen_coverage_btn.grid(row=0, column=3, sticky=tkinter.E)

        self.frame.grid(row=2, sticky=tkinter.E, padx = 8, pady = 8)

class CTestRunnerGui:
    def __init__(self):
        self.tk_root                   = None
        self.dir_sel_frame:DirectorySelectingFrame = None
        self.module_msg_frame:ModuleListAndMessageFrame = None
        self.button_frame:TestButtonFrame = None

    def __update_module_list_dispayed(self):
        module_dir = self.dir_sel_frame.get_test_module_dir()
        self.module_msg_frame.update_module_list(module_dir)

    def __get_run_test_param(self, run_type):
        test_param = RunTestParam()
        test_param.modules                = self.module_msg_frame.get_module_list()
        test_param.run_type               = run_type
        test_param.global_config_path     = self.dir_sel_frame.get_global_config_file_path()
        test_param.test_directory         = self.dir_sel_frame.get_test_module_dir()
        test_param.test_harness_directory = self.dir_sel_frame.get_test_harness_dir()
        test_param.text_out               = self.module_msg_frame.text_out
        return test_param

    def create(self, run_func, gen_func):
        self.tk_root = Tk()
        self.tk_root.title('C Test Runner')
        self.tk_root.grid_columnconfigure(0, weight=1)

        # Create directory path selection frame
        self.dir_sel_frame = DirectorySelectingFrame(self.tk_root)
        self.dir_sel_frame.set_update_end_hook(
            self.__update_module_list_dispayed
        )
        self.dir_sel_frame.create()

        # Module list and Message window frame
        self.module_msg_frame = ModuleListAndMessageFrame(self.tk_root)
        self.module_msg_frame.create()
        self.__update_module_list_dispayed()

        # Button frame
        def clear_run():
            test_param = self.__get_run_test_param("Clear")
            run_func(test_param)
        def make_run():
            test_param = self.__get_run_test_param("Make")
            run_func(test_param)
        def build_run():
            test_param = self.__get_run_test_param("Build")
            run_func(test_param)
        def gen_run():
            init_dir = self.dir_sel_frame.get_test_module_dir()
            in_dir   = filedialog.askdirectory(initialdir=init_dir,title="Select source and test code directory")
            open_dir = filedialog.askdirectory(initialdir=init_dir, title="Select output directory")
            if open_dir != "":
                gen_func(in_dir, open_dir)
        self.button_frame = TestButtonFrame(self.tk_root)
        self.button_frame.create(clear_run, make_run, build_run, gen_run)
        self.button_frame.set_test_start_hook(self.module_msg_frame.clear_text)
        self.tk_root.mainloop()
