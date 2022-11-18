'''
 This module provids functions which compares timestamp of the files.
'''
import os
from enum import Enum
from typing import List

###############################################
####### Definitions of Constant values ########
###############################################

# Return value of 'CompareTimestamps'
class CompResult(Enum):
    '''
     This is enumlator indicating the result of the comparison between files.
    '''
    FILE1_IS_NEWER = 0
    FILE2_IS_NEWER = 1
    SAME_TIMESTAMP = 2

class TimestampComp:
    '''
     This module provids functions which compares timestamp of the files.
    '''
    # Initialize time stamp list. For more explanation, see where this is
    # defined.
    # This hash will have the file paths as keys, and the value will be the
    # time stamp value of the file.
    # That is, the time stamp value of the file will be saved in this hash not
    # to call system function every time to check the time stamp value.
    __save_time_stamp_dict = {}

    @classmethod
    def __get_time_stamp_value_from_os(cls, file:str) -> float:
        """
         This function returns comparable time stamp value of the input file.
        file: The input file path
        """

        # Get the status of the file
        # Return the value
        return os.path.getmtime(file)

    @classmethod
    def get_timestamp_value(cls, file:str) -> float:
        """
        This function returns the time stamp value of the input file.
        If the '__SavedTimeStampDict' has the time stamp value of the input file,
        it returns from the hash. Unless, it will check the system file stamp value.
        file: The input file path
        """

        # Has the time stamp value of the file been stored?
        if file in cls.__save_time_stamp_dict:
            # Return the value from the hash.
            return cls.__save_time_stamp_dict[file]
        # Get the value from the system
        file_time = cls.__get_time_stamp_value_from_os(file)

        # Save the file time to the hash.
        cls.__save_time_stamp_dict[file] = file_time

        # Return the value
        return file_time

    @classmethod
    def compare_timestamps(cls, file1:str, file2:str) -> CompResult:
        """
         This function compares the time stamps of the input files.
         Returns 'FILE1_IS_NEW', if the time stamp value of the file in the first input is larger.
         Returns 'FILE2_IS_NEW', if the time stamp value of the file in the second input is larger.
        Returns 'SAME_TIMESTAMP', if the time stamp value of the two files are the same.

        Args:
            file1 (str): file path to be compared
            file2 (str): another file path to be compared

        Returns:
            CompResult: result of the comparison
        """

        # Get the time stamp value of the first input file.
        timestame_value1 = cls.get_timestamp_value(file1)

        # Get the time stamp value of the second input file.
        timestame_value2 = cls.get_timestamp_value(file2)

        # If the time stamp value of the second input file is larger...
        if timestame_value1 < timestame_value2:
            # The second input file is newer.
            return CompResult.FILE2_IS_NEWER

        # If the time stamp value of the first input file is larger...
        if timestame_value1 > timestame_value2:
            # The first input file is newer.
            return CompResult.FILE1_IS_NEWER

        # Else, they have the same time stamp value.
        return CompResult.SAME_TIMESTAMP

    @classmethod
    def is_the_file_latest(cls, in_file:str, list_file:List[str])->bool:
        """
        This function checks if the first input file is the latest compared
        to the files in the list input as the second parameter.
        inFile: The file to be checked.
        aFileList_ref: Reference to the array containing files to be compared.
        """

        # Check the file with all files in the array
        for file_compared in list_file :
            # If a file in the array is newer,
            if cls.compare_timestamps(in_file, file_compared) == CompResult.FILE2_IS_NEWER:
                # Return false
                return False

        # Reaching here means the checked file is the newest one.
        return True

    @classmethod
    def is_the_file_oldest(cls,in_file:str, list_file:List[str])->bool:
        """
        This function checks if the first input file is the latest compared
        to the files in the list input as the second parameter.
        inFile: The file to be checked.
        aFileList_ref: Reference to the array containing files to be compared.
        """

        # Check the file with all files in the array
        for file_compared in list_file :
            # If a file in the array is newer,
            if cls.compare_timestamps(in_file, file_compared) == CompResult.FILE1_IS_NEWER:
                # Return false
                return False

        # Reaching here means the checked file is the oldest one.
        return True

    @classmethod
    def clear_time_stamp_dict(cls) -> None:
        """
        This function clears saved timestamp information. Intended to be used for test
        """

        cls.__save_time_stamp_dict = {}
