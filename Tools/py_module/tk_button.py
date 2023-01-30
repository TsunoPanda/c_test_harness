'''
 This module provids tk buttons which has extra functionality.
'''
import time
import tkinter
from tkinter import Tk
from tkinter import ttk
from tkinter import messagebox
import threading

class LockAcquireFailError(Exception):
    ''' This class represents an error that should be raised when lock cant' be acquired 
        in "task_start_hook" in "MultiTaskButton".
    '''


class MultiTaskButton(ttk.Button):
    def __init__(self, frame, text, task):
        super().__init__(frame, text = text, command = lambda: self.__call_back())
        self.task              = task
        self.task_start_hook   = None
        self.task_end_hook     = None
        self.task_ex_hook      = lambda ex: print(ex)
        self.exception_hook    = lambda ex: print(ex)
        self.acquire_fail_hook = lambda ex: print(ex)

    def __task(self):
        try:
            self.task()
        except Exception as ex:
            if self.task_ex_hook is not None:
                self.task_ex_hook(ex)
        finally:
            if self.task_end_hook is not None:
                self.task_end_hook()

    def __call_back(self):
        try:
            if self.task_start_hook is not None:
                self.task_start_hook()

            if self.task is None:
                raise UnboundLocalError('The call back task is not defined.')

            thread = threading.Thread(
                target = self.__task,
            )
            thread.start()

        except LockAcquireFailError as ex:
            if self.acquire_fail_hook is not None:
                self.acquire_fail_hook(ex)

        except Exception as ex:
            if self.exception_hook is not None:
                self.exception_hook(ex)

    def set_task_start_hook(self, hook):
        self.task_start_hook = hook

    def set_task_end_hook(self, hook):
        self.task_end_hook = hook

    def set_task_exception_hook(self, hook):
        self.task_ex_hook = hook

    def set_exception_hook(self, hook):
        self.exception_hook = hook

    def set_acquire_fail_hook(self, hook):
        self.acquire_fail_hook = hook

if __name__ == "__main__":
    def show_msg_box1():
        time.sleep(3)
        messagebox.showinfo("button was pushed", "3 second passed after you clicked the button1")
    def show_msg_box2():
        time.sleep(3)
        messagebox.showinfo("button was pushed", "3 second passed after you clicked the button2")

    lock = threading.Lock()
    def start_hook():
        if lock.acquire(blocking = False) is False:
            raise LockAcquireFailError('The previous task is working')

    def end_hook():
        lock.release()

    def exception_hook(ex):
        print(ex)
        lock.release()


    root = Tk()
    root.title('Button test')

    frame1 = ttk.Frame(root, relief='groove', padding = 10)
    frame1.pack()

    button1 = MultiTaskButton(frame1, text = 'button1', task = show_msg_box1)
    button1.grid(row=0, column = 0)
    button1.set_task_start_hook(start_hook)
    button1.set_task_end_hook(end_hook)
    button1.set_exception_hook(exception_hook)

    button2 = MultiTaskButton(frame1, text = 'button2', task = show_msg_box2)
    button2.grid(row=0, column = 1)
    button2.set_task_start_hook(start_hook)
    button2.set_task_end_hook(end_hook)
    button2.set_exception_hook(exception_hook)

    root.mainloop()
