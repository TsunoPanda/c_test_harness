import os
from enum import Enum
from typing import List

###############################################
####### Definitions of Constant values ########
###############################################

# Return value of 'CompareTimestamps'
class CompResult(Enum):
    FILE1_IS_NEWER = 0
    FILE2_IS_NEWER = 1
    SAME_TIMESTAMP = 2

# Initialize time stamp list. For more explanation, see where this is
# defined.
# This hash will have the file paths as keys, and the value will be the
# time stamp value of the file.
# That is, the time stamp value of the file will be saved in this hash not
# to call system function every time to check the time stamp value.
__SavedTimeStampDict = {}

def __GetTimeStampValueFromOs(file:str) -> float:
    """
    This function returns comparable time stamp value of the input file.
    file: The input file path
    """

    # Get the status of the file
    # Return the value
    return os.path.getmtime(file)

def GetTimeStampValue(file:str) -> float:
    """
    # This function returns the time stamp value of the input file.
    # If the '__SavedTimeStampDict' has the time stamp value of the input file,
    # it returns from the hash. Unless, it will check the system file stamp value.
    # file: The input file path
    """

    # Has the time stamp value of the file been stored?
    if file in __SavedTimeStampDict:
        # Return the value from the hash.
        return __SavedTimeStampDict[file]
    else:
        # Get the value from the system
        file_time = __GetTimeStampValueFromOs(file)

        # Save the file time to the hash.
        __SavedTimeStampDict[file] = file_time

        # Return the value
        return file_time;

def CompareTimestamps(file1:str, file2:str) -> CompResult:
    """
    # This function compares the time stamps of the input files.
    # Returns 'FILE1_IS_NEW', if the time stamp value of the file in the first input is larger.
    # Returns 'FILE2_IS_NEW', if the time stamp value of the file in the second input is larger.
    # Returns 'SAME_TIMESTAMP', if the time stamp value of the two files are the same.
    # file1: The input file path of the first input
    # file2: The input file path of the second input
     """

    # Get the time stamp value of the first input file.
    timestameValue1 = GetTimeStampValue(file1)

    # Get the time stamp value of the second input file.
    timestameValue2 = GetTimeStampValue(file2)

    # If the time stamp value of the second input file is larger...
    if (timestameValue1 < timestameValue2):
        # The second input file is newer.
        return CompResult.FILE2_IS_NEWER

    # If the time stamp value of the first input file is larger...
    elif (timestameValue1 > timestameValue2):
        # The first input file is newer.
        return CompResult.FILE1_IS_NEWER
    else:
        # Else, they have the same time stamp value.
        return CompResult.SAME_TIMESTAMP

def IsTheFileLatest(inFile:str, lFiles:List[str])->bool:
    """
    # This function checks if the first input file is the latest compared
    # to the files in the list input as the second parameter.
    # inFile: The file to be checked.
    # aFileList_ref: Reference to the array containing files to be compared.
    """

    # Check the file with all files in the array
    for fileCompared in lFiles :
        # If a file in the array is newer,
        if CompareTimestamps(inFile, fileCompared) == CompResult.FILE2_IS_NEWER:
            # Return false
            return False

    # Reaching here means the checked file is the newest one.
    return True

def ClearTimeStampDict() -> None:
    """
    This function clears saved timestamp information. Intended to be used for test
    """

    global __SavedTimeStampDict
    __SavedTimeStampDict = {}

if __name__ == "__main__":

    file1 = 'TimeStampComp.py'
    file2 = 'Makefile.py'

    mtime = GetTimeStampValue(file1)
    mtime2 = GetTimeStampValue(file2)
    print(mtime)
    print(mtime2)

    if CompareTimestamps(file1, file2) == CompResult.FILE1_IS_NEWER:
        print (file1+' is newer')
    else:
        print (file2+' is newer')

    file_list = [file1, file2]
    if IsTheFileLatest(file1, file_list):
        print (file1+ ' is the latest')
    else:
        print (file1+ ' is not the latest')



