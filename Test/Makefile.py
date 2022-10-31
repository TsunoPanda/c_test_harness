import os
import re
import subprocess
import TimeStampComp
from enum import Enum
from typing import List
import dataclasses

# Return value of 'Makefile.Make' and 'Makefile.Build'
class ExecutableStatus(Enum):
    EXECUTABLE_VALID   = 0
    EXECUTABLE_INVALID = 1

class MakeFile:

    # Return value of 'IssueCompileCommand'
    class CompileStatus(Enum):
        COMPILE_SUCCEEDED = 0
        COMPILE_ERROR     = 1

    # Return value of 'LinkObjects'
    class LinkStatus(Enum):
        LINK_SKIPPED   = 0
        LINK_SUCCEEDED = 1
        LINK_ERROR     = 2

    # Return value of 'CompileSources'
    class WholeCompileStatus(Enum):
        NO_COMPILED_FILE           = 0
        NO_COMPILE_ERROR           = 1
        AT_LEAST_ONE_COMPILE_ERROR = 2

    @dataclasses.dataclass
    class RelevantFiles:
        src: str
        obj: str
        dep: str
        opt: str

    def __init__(self, targetPath:str, compiler:str, lIncludePath:List[str], lLinkerOption:List[str]):
        """
        This function initializes all global variables in this module
        targetPath: Path to the target executable file
        compiler: Compiler command e.g. 'gcc'
        lIncludePath: 
        lLinkerOption:
        """

        # Compiler to be used
        # Save the compiler command into a global variable
        self.__Compiler:str = compiler

        # Target executable file path
        # Save the target file path into a global variable
        self.__TargetPath:str = targetPath

        # Include arguments in the compiling command. This will be generated from the '@gaIncludePaths'.
        # Initialize include arguments
        self.__IncludeString:str = self.__IncludePathArrayToCommand(lIncludePath)

        # Option arguments in the compiling command. This will be generated from the '@gaOptions'.
        self.__LinkerOptionString:str = self.__OptionArrayToCommand(lLinkerOption)

        # This is an array of RelevantFiles
        # the respective values are 'source file path', 'object file path', 'dependency file path', 'option string'
        # for all sources files to be compiled.
        self.__AllRelevantFiles:List[RelevantFiles] = []

    def __std_output(self, msg:str):
        print(msg, end='')

    def __OptionArrayToCommand(self, lOption:List[str])->str:
        """
        This function converts the array of the options into the string which can be used in the command.
        e.g. ["-Wall", "-O2", "-MMD"] -> "-Wall -O2 -MMD"
        """

        # Combine the members of the list with separator ' '.
        return ' '.join(lOption)

    def __IncludePathArrayToCommand(self, lIncludePath:List[str])->str:
        """
        This function converts the array of the include paths into the string which can be used in the command.
        e.g. ["../ProductCode/SetAndGet/", "./TestHarness/"] -> "-I ../ProductCode/SetAndGet/ -I ./TestHarness/"
        """

        # Make the array which will have include options as members.
        # e.g ["../ProductCode/SetAndGet/", "./TestHarness/"]
        #  -> ["-I ../ProductCode/SetAndGet/", "-I ./TestHarness/"]
        lIncludeOptions = map(lambda s: '-I ' + s, lIncludePath)

        # Get the option string by inputting the option array to 'OptionArrayToCommand', and return the result.
        return self.__OptionArrayToCommand(lIncludeOptions)

    def __CheckSourceFile(self, filePath:str)->(bool, str):
        basename = os.path.basename(filePath)
        filename, ext = os.path.splitext(basename)
        if (ext == '.c') or (ext == '.cpp'):
            return (True, filename)
        else:
            return (False, filename)

    def __MakeAllRelevantFileDict(self, lSourceFile:List[str], lOption:List[str], objPath:str) -> List[RelevantFiles]:
        """
        This function makes the global array 'gaAllRelevantFiles' which has all relevant file paths
        aSourceFiles_ref: Reference to the array which all the source files
        objPath: # Path to a folder where all object files are stored
        """

        # Create an anonymous array for all relevant files
        lAllRelevantFiles = []

        # Make all the relevant file array for each source file
        for i_cFile in lSourceFile:
            # Check if the source file has a good format.
            is_C_file, fileName = self.__CheckSourceFile(i_cFile)
            if is_C_file == True :

                # Initialize the relevant file object
                dRlevantFile = self.RelevantFiles(
                    src = i_cFile,
                    obj = objPath + '/' + fileName + '.o',
                    dep = objPath + '/' + fileName + '.d',
                    opt = self.__OptionArrayToCommand(lOption)
                    )

                # Push the anonymous hash into the global array
                lAllRelevantFiles.append(dRlevantFile)
            else:
                # The input .c source file has a bad format. Display the warning message.
                self.__std_output('Warning: The way to define the c file is not correct.\n');
                self.__std_output('>>> ' + i_cFile + '\n');

        return lAllRelevantFiles

    def __CreateObjectFolder(self, objPath:str):
        """
        This function creates the folder where all object files to be generated will be saved.
        $objPath: Path to a folder where all object files are stored
        """

        # Save the object file path temporarily.
        objTmp = objPath;

        # Replace '/' into '\'. This is required for the windows shell.
        objTmp = re.sub('/', r'\\', objTmp)

        # If NOT the object folder exists, then, make it.
        subprocess.check_output('if not exist '+ objTmp + ' mkdir ' + objTmp, shell=True)

    def __ErrorInTheMessage(self, msg:str) :
        """
        This function detects error by checking the received message.
        """

        # Check if the message contains "error"
        # May need to improve
        error = re.compile(r'error')
        result = error.search(msg)
        if result is not None:
            return True
        else:
            return False

    def __IssueCompileCommand(self, cCompiler:str, includeStr:str, dRelevantFile:RelevantFiles)->CompileStatus:
        """
        This function issues the compiling command according to the input parameters.
        This also displays the command and the output result.
        If this function detected 'error' in the output message of the command, it returns 'COMPILE_ERROR'.
        Unless, returns 'COMPILE_SUCCEEDED'.
        cCompiler: Compiler command e.g. 'gcc'
        includeStr: Include string e.g. '-I ./hoge/'
        dRelevantFile: Reference to a hash which has source, object, dependency file path
        """

        optionStr = dRelevantFile.opt

        # Make compiling command
        compile_cmd = cCompiler + " " + optionStr + " " + includeStr + " -c " + dRelevantFile.src + " -o " + dRelevantFile.obj

        # Adding '2>&1' means send stderr(2) to the same place as stdout (&1))
        compile_cmd = compile_cmd + ' 2>&1'

        # Display the command.
        self.__std_output(compile_cmd + '\n')

        # Execute the command and get the STDOUT.
        # Execute the command and get the output as binary
        try:
            wholeMsgByte = subprocess.check_output(compile_cmd,
                                                   stderr=subprocess.STDOUT,
                                                   shell=True)
        except subprocess.CalledProcessError as e:
            self.__std_output("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        # Convert the binary into string
        wholeMsg = wholeMsgByte.decode()

        # Display the result.
        self.__std_output(wholeMsg);

        # Check if the result text contain 'error'
        if self.__ErrorInTheMessage(wholeMsg) == True:
            # Error message detected.
            return self.CompileStatus.COMPILE_ERROR
        else:
            # No error message detected.
            return self.CompileStatus.COMPILE_SUCCEEDED

    def __DoesTheFileNeedToBeCompiled(self, dRelevantFile:RelevantFiles)->bool:
        """
        This function check if the input file needs to be compiled or it does not.
        Return TRUE: If input file needs to be compiled.
        Return FALSE: If input file dose not need to be compiled.
        hRelevantFile_ref: Reference to a hash which has source, object, dependency file path
        """

        # Get the object file path from the hash
        objectFile     = dRelevantFile.obj

        # Get the dependency file path from the hash
        dependancyFile = dRelevantFile.dep

        # Are both the object/dependency files exist?
        if os.path.exists(objectFile) and os.path.exists(dependancyFile):
            # Get the array which contains all the relational files to the source file.
            aRelatedFileList = self.__GetRelatedFileList(dependancyFile)

            # Is the object files newest compared to all the relative files?
            if TimeStampComp.IsTheFileLatest(objectFile, aRelatedFileList) == True:
                # Yes, the object file is up-to-date, skip the compiling.
                return False
            else:
                # One of the relative file is updated. Compile the source file.
                return True
        else:
            # One of the object/dependency files does not exist.
            # Then, compile the file.
            return True

    def __GetDirectry(self, filePath:str)->str:
        return os.path.dirname(filePath)


    def __CompileSources(self, compiler:str, includeStr:str)->WholeCompileStatus:
        """
        This function compile all the source files listed in the global array 'gaAllRelevantFiles'.
        If the object file is already exist and it is the latest, this skips the compilation.
        Returns NO_COMPILE_ERROR: If compilation finished without error.
        Returns AT_LEAST_ONE_COMPILE_ERROR: If at least one file finished with an error.
        Returns NO_COMPILED_FILE: If no file has been compiled.
        compiler: Compiler command e.g. 'gcc'
        aAllRelevantFiles_ref: Reference to the array which will contains all source, object, dependency file paths.
        includeStr: Include string e.g. '-I ./hoge/'
        """

        # Initialize the compile error indicator.
        # This value will be TRUE if at least one compile error happened.
        IsCompileErrorExist = False

        # Initialize the file compile indicator.
        # This value will be TRUE if at least one file was compiled.
        IsCompiledFileExist = False

        # Start compiling for all source files in the array
        for dRelativeFiles in self.__AllRelevantFiles:
            # If the source file does NOT exists
            if os.path.exists(dRelativeFiles.src) == False:
                # The source file was not found
                self.__std_output("Error: Could not find " + dRelativeFiles.src + '\n')

                # Error detected, set the error indicator 'TRUE'
                IsCompileErrorExist = True

            # Check if the source file needs to be compiled
            elif self.__DoesTheFileNeedToBeCompiled(dRelativeFiles) == True:
                # The file need to be compiled

                # Capture object file folder path
                objPath = self.__GetDirectry(dRelativeFiles.obj)

                # If not exists, Create a folder where all object files will be stored.
                self.__CreateObjectFolder(objPath)

                # Set the compile indicator 'TRUE'
                IsCompiledFileExist = True

                # Issue the compile command and check if it outputs error.
                if self.__IssueCompileCommand(compiler, includeStr, dRelativeFiles) == self.CompileStatus.COMPILE_ERROR:
                    # Error detected, set the error indicator 'TRUE'
                    IsCompileErrorExist = True

            else:
                # The source file does not need to be compiled. skip.
                self.__std_output('skip compiling ' + dRelativeFiles.obj + '\n')

        # Check the Compiling result
        # Error exists?
        if IsCompileErrorExist == True:
            # Error has happened
            return self.WholeCompileStatus.AT_LEAST_ONE_COMPILE_ERROR

        # Compiled file exist?
        if IsCompiledFileExist == True:
            # Some files are compiled without any errors
            return self.WholeCompileStatus.NO_COMPILE_ERROR
        else:
            # No files has been compiled.
            return self.WholeCompileStatus.NO_COMPILED_FILE

    def __LinkObjects(self, compiler:str, optionStr:str, targetStr:str)->LinkStatus:
        """
        This function links all the object files listed in the global array 'gaAllRelevantFiles'.
        And generates target executable file.
        compiler: Compiler command e.g. 'gcc'
        aAllRelevantFiles_ref: Reference to the array which will contains all source, object, dependency file paths.
        optionStr: Option string e.g. '-Wall -O'
        targetStr:
        """

        # Define/initialize the string which will contain all object file to be linked.
        objectsStr = ""

        # Append all object files in the array
        for dRelevantFile in self.__AllRelevantFiles:
            objectsStr = objectsStr + dRelevantFile.obj + ' '

        # Make the command
        cmd = compiler + ' ' + optionStr + ' -o ' + targetStr + ' ' + objectsStr

        # Adding '2>&1' means send stderr(2) to the same place as stdout (&1))
        cmd += ' 2>&1'

        # Display the command
        self.__std_output(cmd + '\n');

        # Execute the command and get the STDOUT using 'qx//' syntax.
        # Execute the command and get the output as binary
        try:
            wholeMsgByte = subprocess.check_output(cmd,
                                                   stderr=subprocess.STDOUT,
                                                   shell=True)
        except subprocess.CalledProcessError as e:
            self.__std_output("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        # Convert the binary into string
        wholeMsg = wholeMsgByte.decode()

        # Display the result.
        self.__std_output(wholeMsg);

        # Check if the result text contain 'error'
        if self.__ErrorInTheMessage(wholeMsg) == True:
            # Error message detected.
            return self.LinkStatus.LINK_ERROR
        else:
            # No error message detected.
            return self.LinkStatus.LINK_SUCCEEDED

    def __GetRelatedFileList(self, dFilePath:str)->List[str]:
        """
        This function returns the array containing all relative files found in the input .d file
        dFilePath: Dependency file path
        """

        # Define/initialize the array of relative file found in the input .d file
        fileList = []

        # Open the dependency file.
        InFile = open(dFilePath, 'r')

        Lines = InFile.readlines()

        # Read the file line by line.
        for line in Lines:
            # Clean the line string
            # Remove the object file
            line = re.sub(r'.+\:', '', line)
            # Remove '\'
            line = re.sub(r'\\', '', line)
            # Remove a space at the top.
            line = re.sub(r'^\s+', '', line)
            # Remove a space at the bottom.
            line = re.sub(r'\s+$', '', line)

            # Split the line into relevant files
            fileList += re.split(r'\s+', line)

        # Close the dependency file.
        InFile.close()

        # Return the array of the related files
        return fileList

    def __IsLinkingRequiered(self, targetPath:str, compileStates:WholeCompileStatus)->bool:
        """
        This function returns TRUE if the linking required. Returns FALSE if not.
        targetPath: Path to the target executable file
        compileStates: Compile state should be return value of the 'CompileSources'
        """

        # If at least one source file was updated and compiled without error.
        if compileStates == self.WholeCompileStatus.NO_COMPILE_ERROR:
            # Linking is required anyway.
            return True

        # If at least one error happened.
        elif compileStates == self.WholeCompileStatus.AT_LEAST_ONE_COMPILE_ERROR:
            # Skip linking due to the error
            self.__std_output('Skip linking, because at least one compile error happened.\n')
            return False;
        # If no compiled file exists
        else : # compileStates == self.WholeCompileStatus.NO_COMPILED_FILE
            # If the executable exists,
            if os.path.exists('./' + targetPath) == True:
                # Skip linking because no updated source file, and the executable exists.
                self.__std_output('Skip linking, because nothing has been updated.\n')
                return False
            else:
                # No compiled file, but there isn't executable file,
                # then linking is required.
                return True

    def __IsTheExecutableValid(self, compileState:WholeCompileStatus, linkState:LinkStatus)->ExecutableStatus:
        """
        This function decides if there is valid executable generated as
        seeing the compilation state and linking state.
        compileState: Previous Compilation state
        linkState: Previous linking state
        """

        # Check the compilation state
        if compileState == self.WholeCompileStatus.AT_LEAST_ONE_COMPILE_ERROR:
            # Compile failed, then no valid executable anyway
            return(ExecutableStatus.EXECUTABLE_INVALID)

        # Check the linking state
        if linkState == self.LinkStatus.LINK_ERROR:
            # Linking failed, then no valid executable anyway
            return(ExecutableStatus.EXECUTABLE_INVALID)

        # No error, then the execute file is valid
        return(ExecutableStatus.EXECUTABLE_VALID)

    def AddSrc(self, aSrcFilePath_ref:List[str], aOption_ref:List[str], objPath:str):
        """
        aSrcFilePath_ref: 
        aOption_ref:
        objPath:
        """

        # Initialize an array which will contains all source, object, dependency file paths.
        # For more explanation, see where this is defined.
        self.__AllRelevantFiles += self.__MakeAllRelevantFileDict(aSrcFilePath_ref, aOption_ref, objPath)

    def Make(self)->ExecutableStatus:
        """
        This function will make target object executable file. But only out-of-date source files are compiled.
        That is, up-to-data files will be skipped to be compiled.
        Linking is also skipped if all the object files are not updated.
        Then return the compile state.
        """

        # Compile all the sources and get the status
        compileState = self.__CompileSources(self.__Compiler, self.__IncludeString)

        linkState = None

        # Check if linking is required
        if self.__IsLinkingRequiered(self.__TargetPath, compileState) == True:
            # If required, then link them
            linkState = self.__LinkObjects(self.__Compiler, self.__LinkerOptionString, self.__TargetPath)
        else:
            linkState = self.LinkStatus.LINK_SKIPPED

        return self.__IsTheExecutableValid(compileState, linkState)

    def __GetAllFiles(dir_path:str)->List[str]:
        FileList = []

        if dir_path[-1] != '/':
            dir_path += '/' 

        AllInDir = os.listdir(dir_path)
        for FileOrDIr in AllInDir:
            FileOrDIr = dir_path + FileOrDIr
            if(os.path.isfile(FileOrDIr)):
                FileList.append(FileOrDIr)
        return FileList

    def Clear(self):
        """
        This function removes all the object/dependency files in the object folder.
        Removes the target executable file as well.
        """
        for hAllRelevantFiles_ref in self.__AllRelevantFiles:
            objPath = self.__GetDirectry(hAllRelevantFiles_ref.obj)

            # Get the list of all files in the object path
            afiles = self.__GetAllFiles(objPath)

            # Remove all files in the object directly
            for file in afiles:
                # Remove a file
                os.remove(file);

    def Build(self)->ExecutableStatus:
        """
        This function will compile all source files in any cases.
        Then return the compile state.
        """
        # Removes all the object/dependency files in the object folder.
        self.Clear()

        # Then, make
        return self.Make()

if __name__ == "__main__":
    target = './MakefileTest/test.exe'
    compiler = 'gcc'
    includePath = ['./MakefileTest/math']
    linkerOption = ['-MMD', '-Wall', '-O2']
    instance = MakeFile(target, compiler, includePath, linkerOption)

    source = ['./MakefileTest/main.c', './MakefileTest/math/math.c']
    compileOption = ['-MMD', '-Wall', '-O2']
    objPath = './MakefileTest/Obj'
    instance.AddSrc(source, compileOption, objPath)

    instance.Make()


