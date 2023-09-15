'''
 This module provids tk buttons which has extra functionality.
'''
from tkinter import Tk
from tkinter import ttk
from tkinter import messagebox
import threading

class LockAcquireFailError(Exception):
    ''' This class represents an error that should be raised when lock cant' be acquired
        in "task_start_hook" in "MultiTaskButton".
    '''

class MultiTaskButton(ttk.Button): # pylint: disable=too-many-ancestors
    ''' This class represents a button. This can have a task witch starts running when the button
        was clicked. And the task will be worked in another thread. Thus, it doesn't disturb
        main loop.
    '''

    def __init__(self, frame, text, task):
        # pylint: disable=unnecessary-lambda
        super().__init__(frame, text = text, command = lambda: self.__call_back())
        self.task              = task
        self.task_start_hook   = None
        self.task_end_hook     = None
        self.task_ex_hook      = print
        self.exception_hook    = print
        self.acquire_fail_hook = print

    def __task(self):
        try:
            self.task()
        except Exception as ex: # pylint: disable=broad-except
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

        except Exception as ex: # pylint: disable=broad-except
            if self.exception_hook is not None:
                self.exception_hook(ex)

    def set_task_start_hook(self, hook):
        ''' This method sets the hook function to be executed
        immediately before the task is executed.
        '''
        self.task_start_hook = hook

    def set_task_end_hook(self, hook):
        ''' This method sets the hook function to be executed
        immediately after the task was finished.
        '''
        self.task_end_hook = hook

    def set_task_exception_hook(self, hook):
        ''' This method sets the hook function to be executed
        when the exception happened while executing the task.
        '''
        self.task_ex_hook = hook

    def set_exception_hook(self, hook):
        ''' This method sets the hook function to be executed
        when the exception happened while trying to execute the task.
        '''
        self.exception_hook = hook

    def set_acquire_fail_hook(self, hook):
        ''' This method sets the hook function to be executed
        when the "LockAcquireFailError" exception was arisen in the task.
        '''
        self.acquire_fail_hook = hook

if __name__ == "__main__":
    # Because this is GUI module, the test and example code are written here as a main function
    # Creates GUI including two buttons. If click one of the buttons, after 3 seconds, a message
    # box will be shown with a message. During the 3 seconds, user can click the buttons, but they
    # won't work. because the resources are locked.
    import time

    def show_msg_box1():
        ''' A message box will be shown after 3 seconds from calling this function
        '''
        time.sleep(3)
        messagebox.showinfo("button was pushed", "3 second passed after you clicked the button1")

    def show_msg_box2():
        ''' A message box will be shown after 3 seconds from calling this function
        '''
        time.sleep(3)
        messagebox.showinfo("button was pushed", "3 second passed after you clicked the button2")

    # Define a lock object
    lock = threading.Lock()

    def start_hook():
        ''' This function is a task start hook function. This will check the acquisition of
        the lock object. If it was locked, arises LockAcquireFailError exception.
        '''
        if lock.acquire(blocking = False) is False: # pylint: disable=consider-using-with
            raise LockAcquireFailError('The previous task is working')

    def end_hook():
        ''' This function is a task end hook function. This will release the lock object which was
        acquired by the start_hook function
        '''
        lock.release()

    def exception_hook(ex):
        ''' This exception hook function which will be called when the exception happened
        while trying to execute the task. This will release the lock object as well.
        '''
        print(ex)
        lock.release()

    # Define the root object of the TK
    root = Tk()
    root.title('Button test')

    # Define the frame object
    frame1 = ttk.Frame(root, relief='groove', padding = 10)
    frame1.pack()

    # Define Button 1
    button1 = MultiTaskButton(frame1, text = 'button1', task = show_msg_box1)
    button1.grid(row=0, column = 0)
    button1.set_task_start_hook(start_hook)
    button1.set_task_end_hook(end_hook)
    button1.set_exception_hook(exception_hook)

    # Define Button 2
    button2 = MultiTaskButton(frame1, text = 'button2', task = show_msg_box2)
    button2.grid(row=0, column = 1)
    button2.set_task_start_hook(start_hook)
    button2.set_task_end_hook(end_hook)
    button2.set_exception_hook(exception_hook)

    # Start main loop
    root.mainloop()
