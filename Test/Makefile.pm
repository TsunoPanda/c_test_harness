package Makefile;
use strict;
use feature 'state';
use lib qw(./);
use Exporter;
use TimeStampComp;

our @ISA = qw(Exporter);
our @EXPORT = qw(Makefile_Init Makefile_Make Makefile_Clear Makefile_Build);
our @EXPORT_OK = ('EXECUTABLE_VALID', 'EXECUTABLE_INVALID');


# This is an array where the hashes to be saved. The hashes has 'src', 'obj', 'dep' as keys and 
# the respective values are 'source file path', 'object file path', 'dependency file path'
# for all sources files to be compiled.
our @gaAllRelevantFiles   = ();

# Option arguments in the compiling command. This will be generated from the '@gaOptions'.
our $gOptionString        = "";

# Include arguments in the compiling command. This will be generated from the '@gaIncludePaths'.
our $gIncludeString       = "";

# Compiler to be used
our $gCompiler = "";

# Target executable file path
our $gTargetPath = "";

# Path to a folder where all object files are stored
our $gObjPath = "";

###############################################
####### Definitions of Constant values ########
###############################################
# Generic used value. false and true
use constant FALSE => (1==0);
use constant TRUE  => (0==0);

# Return value of 'IssueCompileCommand'
use constant COMPILE_SUCCEEDED => 0;
use constant COMPILE_ERROR     => 1;

# Return value of 'LinkObjects'
use constant LINK_SKIPPED   => 0;
use constant LINK_SUCCEEDED => 1;
use constant LINK_ERROR     => 2;

# Return value of 'CompileSources'
use constant NO_COMPILED_FILE           => 0;
use constant NO_COMPILE_ERROR           => 1;
use constant AT_LEAST_ONE_COMPILE_ERROR => 2;

# Return value of 'Makefile_Make' and 'Makefile_Build'
use constant EXECUTABLE_VALID => 0;
use constant EXECUTABLE_INVALID => 1;


# This function converts the array of the options into the string which can be used in the command.
# e.g. ["-Wall", "-O2", "-MMD"] -> "-Wall -O2 -MMD"
sub OptionArrayToCommand
{
    # $aOptionArray_ref: Reference to the array of the options.
    my ($aOptionArray_ref) = @_;

    # Define/initialize the option string to be returned
    my $optionStr = "";

    # Make the option string by appending all the options in the array
    foreach my $iOptionStr (@{$aOptionArray_ref})
    {
        # Append an option into the option string
        $optionStr = $optionStr.$iOptionStr." ";
    }

    # Chop the last space
    chop($optionStr);

    # Return the option string
    return $optionStr;
}

# This function converts the array of the include paths into the string which can be used in the command.
# e.g. ["../ProductCode/SetAndGet/", "./TestHarness/"] -> "-I ../ProductCode/SetAndGet/ -I ./TestHarness/"
sub IncludePathArrayToCommand
{
    # $aIncludePath_ref: Reference to the array of the include paths
    my ($aIncludePath_ref) = @_;

    # Define/initialize the array which will have include options as members.
    # e.g ["-I ../ProductCode/SetAndGet/", "-I ./TestHarness/"]
    my @includeOptions = ();

    # Make the include option array from the include path array.
    # e.g. ["../ProductCode/SetAndGet/", "./TestHarness/"] -> ["-I ../ProductCode/SetAndGet/", "-I ./TestHarness/"]
    foreach my $i_inPath (@{$aIncludePath_ref})
    {
        # Pushing an include path with adding '-I ' at the top of the path.
        push(@includeOptions, "-I ".$i_inPath);
    }

    # Get the option string by inputting the option array to 'OptionArrayToCommand', and return the result.
    return OptionArrayToCommand(\@includeOptions);
}

# This function makes the global array 'gaAllRelevantFiles' which has all relevant file paths
# in accordance with the global variables '@gaSourceFiles' and '$gObjPath'.
sub MakeAllRelevantFileHash
{
    # $aSourceFiles_ref: Reference to the array which all the source files
    # $objPath: # Path to a folder where all object files are stored
    my ($aSourceFiles_ref, $objPath) = @_;

    # Create an anonymous array for all relevant files
    my $aAllRelevantFiles_ref = [];

    # Make all the relevant file array for each source file
    foreach my $i_cFile (@{$aSourceFiles_ref})
    {
        # Check if the source file has a good format.
        # (TODO: Now it allows only .c file. .cpp files should be considered in the future.)
        if ($i_cFile =~ /.*(\/.+)\.c/)
        {
            # Initialize the anonymous relevant file hash.
            my $hRlevantFile_ref = {'src' => "", 'obj' => "", 'dep' => ""};

            # Set the source file path with the key 'src'
            $hRlevantFile_ref->{'src'} = $i_cFile;

            # Set the object file path with the key 'obj'
            $hRlevantFile_ref->{'obj'} = $objPath.$1.".o";

            # Set the dependency file path with the key 'dep'
            $hRlevantFile_ref->{'dep'} = $objPath.$1.".d";

            # Push the anonymous hash into the global array
            push(@{$aAllRelevantFiles_ref}, $hRlevantFile_ref);
        }
        else
        {
            # The input .c source file has a bad format. Display the warning message.
            printf("Warning: The way to define the c file is not correct.\n");
            printf(">>> ".$i_cFile."\n");
        }
    }

    return @{$aAllRelevantFiles_ref};
}

# This function creates the folder where all object files to be generated will be saved.
sub CreateObjectFolder
{
    # $objPath: Path to a folder where all object files are stored
    my ($objPath) = @_;

    # Save the object file path temporarily.
    my $objTmp = $objPath;

    # Replace '/' into '\'. This is required for the window shell.
    $objTmp =~ s/\//\\/g;

    # If NOT the object folder exists, then, make it.
    system("if not exist ".$objTmp." mkdir ".$objTmp);
}

# This function issues the compiling command according to the input parameters.
# This also displays the command and the output result.
# If this function detected 'error' in the output message of the command, it returns 'COMPILE_ERROR'.
# Unless, returns 'COMPILE_SUCCEEDED'.
sub IssueCompileCommand
{
    # $cCompiler: Compiler command e.g. 'gcc'
    # $optionStr: Option string e.g. '-Wall -O'
    # $includeStr: Include string e.g. '-I ./hoge/'
    # $hRelevantFile_ref: Reference to a hash which has source, object, dependency file path
    my ($cCompiler, $optionStr, $includeStr, $hRelevantFile_ref) = @_;

    # Make compiling command
    my $compile_cmd = $cCompiler." ".$optionStr." ".$includeStr." -c ".$hRelevantFile_ref->{src}." -o ".$hRelevantFile_ref->{obj};

    # Adding '2>&1' means send stderr(2) to the same place as stdout (&1))
    $compile_cmd = $compile_cmd.' 2>&1';

    # Display the command.
    printf($compile_cmd."\n");

    # Execute the command and get the STDOUT using 'qx//' syntax.
    my $output = qx/$compile_cmd/;

    # Display the result.
    printf($output);

    # Check if the result text contain 'error'
    if($output =~ /error/)
    {
        # Error message detected.
        return COMPILE_ERROR;
    }
    else
    {
        # No error message detected.
        return COMPILE_SUCCEEDED;
    }
}

# This function check if the input file needs to be compiled or it does not.
# Return TRUE: If input file needs to be compiled.
# Return FALSE: If input file dose not need to be compiled.
sub DoesTheFileNeedToBeCompiled
{
    # $hRelevantFile_ref: Reference to a hash which has source, object, dependency file path
    my ($hRelevantFile_ref) = @_;

    # Get the object file path from the hash
    my $objectFile     = $hRelevantFile_ref->{obj};

    # Get the dependency file path from the hash
    my $dependancyFile = $hRelevantFile_ref->{dep};

    # Are both the object/dependency files exist?
    if (-e $objectFile && -e $dependancyFile)
    {
        # Get the array which contains all the relational files to the source file.
        my @aRelatedFileList = GetRelatedFileList($dependancyFile);

        # Is the object files newest compared to all the relative files?
        if(TimeStampComp_IsTheFileLatest($objectFile, \@aRelatedFileList) == TRUE)
        {
            # Yes, the object file is up-to-date, skip the compiling.
            return FALSE;
        }
        else
        {
            # One of the relative file is updated. Compile the source file.
            return TRUE;
        }
    }
    else
    {
        # One of the object/dependency files does not exist.
        # Then, compile the file.
        return TRUE;
    }
}

# This function compile all the source files listed in the global array 'gaAllRelevantFiles'.
# If the object file is already exist and it is the latest, this skips the compilation.
# Returns NO_COMPILE_ERROR: If compilation finished without error.
# Returns AT_LEAST_ONE_COMPILE_ERROR: If at least one file finished with an error.
# Returns NO_COMPILED_FILE: If no file has been compiled.
sub CompileSources
{
    # $compiler: Compiler command e.g. 'gcc'
    # $aAllRelevantFiles_ref: Reference to the array which will contains all source, object, dependency file paths.
    # $optionStr: Option string e.g. '-Wall -O'
    # $includeStr: Include string e.g. '-I ./hoge/'
    my ($compiler, $aAllRelevantFiles_ref, $optionStr, $includeStr) = @_;

    # Initialize the compile error indicator.
    # This value will be TRUE if at least one compile error happened.
    my $IsCompileErrorExist = FALSE;

    # Initialize the file compile indicator.
    # This value will be TRUE if at least one file was compiled.
    my $IsCompiledFileExist = FALSE;

    # Start compiling for all source files in the array
    foreach my $hRelativeFiles_ref (@{$aAllRelevantFiles_ref})
    {
        # If the source file does NOT exists
        if ((-e $hRelativeFiles_ref->{'src'}) == FALSE)
        {
            # The source file was not found
            printf("Error: Could not find ".$hRelativeFiles_ref->{src}."\n");

            # Error detected, set the error indicator 'TRUE'
            $IsCompileErrorExist = TRUE;
        }
        # Check if the source file needs to be compiled
        elsif(DoesTheFileNeedToBeCompiled($hRelativeFiles_ref) == TRUE)
        {
            # The file need to be compiled

            # Set the compile indicator 'TRUE'
            $IsCompiledFileExist = TRUE;

            # Issue the compile command and check if it outputs error.
            if(IssueCompileCommand($compiler, $optionStr, $includeStr, $hRelativeFiles_ref) == COMPILE_ERROR)
            {
                # Error detected, set the error indicator 'TRUE'
                $IsCompileErrorExist = TRUE;
            }
        }
        else
        {
            # The source file does not need to be compiled. skip.
            printf("skip compiling ".$hRelativeFiles_ref->{obj}."\n");
        }
    }

    # Check the Compiling result
    # Error exists?
    if($IsCompileErrorExist == TRUE)
    {
        # Error has happened
        return AT_LEAST_ONE_COMPILE_ERROR;
    }

    # Compiled file exist?
    if($IsCompiledFileExist == TRUE)
    {
        # Some files are compiled without any errors
        return NO_COMPILE_ERROR;
    }
    else
    {
        # No files has been compiled.
        return NO_COMPILED_FILE;
    }
}

# This function links all the object files listed in the global array 'gaAllRelevantFiles'.
# And generates target executable file.
sub LinkObjects
{
    # $compiler: Compiler command e.g. 'gcc'
    # $aAllRelevantFiles_ref: Reference to the array which will contains all source, object, dependency file paths.
    # $optionStr: Option string e.g. '-Wall -O'
    # $includeStr: Include string e.g. '-I ./hoge/'
    my ($compiler, $gaAllRelevantFiles, $optionStr, $targetStr) = @_;

    # Define/initialize the string which will contain all object file to be linked.
    my $objectsStr = "";

    # Append all object files in the array
    foreach my $hRelevantFile_ref (@{$gaAllRelevantFiles})
    {
        $objectsStr = $objectsStr.$hRelevantFile_ref->{'obj'}." "
    }

    # Make the command
    my $cmd = $compiler." ".$optionStr." -o ".$targetStr." ".$objectsStr;

    # Adding '2>&1' means send stderr(2) to the same place as stdout (&1))
    $cmd = $cmd.' 2>&1';

    # Display the command
    printf($cmd."\n");

    # Execute the command and get the STDOUT using 'qx//' syntax.
    my $output = qx/$cmd/;

    # Display the result.
    printf($output);

    # Check if the result text contain 'error'
    if($output =~ /error/)
    {
        # Error message detected.
        return LINK_ERROR;
    }
    else
    {
        # No error message detected.
        return LINK_SUCCEEDED;
    }
}

# This function returns the array containing all relative files found in the input .d file
sub GetRelatedFileList
{
    # $dFilePath: Dependency file path
    my ($dFilePath) = @_;

    # Define/initialize the array of relative file found in the input .d file
    my @fileList = ();

    # Open the dependency file.
    open(InFile, "< ".$dFilePath) or die("Can't open the dependency file.");

    # Read the file line by line.
    while (my $line = <InFile>)
    {
        # Clean the line string
        $line =~ s/.+\://g; # Remove the object file
        $line =~ s/\\//g; # Remove '/'
        $line =~ s/^ //g; # Remove a space at the top.

        # Split the line into relevant files
        push(@fileList, split(/\s+/, $line));
    }

    # Close the dependency file.
    close(InFile);

    # Return the array of the related files
    return @fileList;
}

# This function returns TRUE if the linking required. Returns FALSE if not.
sub IsLinkingRequiered
{
    # $targetPath: Path to the target executable file
    # $compileStates: Compile state should be return value of the 'CompileSources'
    my ($targetPath, $compileStates) = @_;

    # If at least one source file was updated and compiled without error.
    if($compileStates == NO_COMPILE_ERROR)
    {
        # Linking is required anyway.
        return TRUE;
    }
    # If at least one error happened.
    elsif($compileStates == AT_LEAST_ONE_COMPILE_ERROR)
    {
        # Skip linking due to the error
        printf("Skip linking, because at least one compile error happened.\n");
        return FALSE;
    }
    # If no compiled file exists
    else # $compileStates == NO_COMPILED_FILE
    {
        # If the executable exists,
        if(-e './'.$targetPath)
        {
            # Skip linking because no updated source file, and the executable exists.
            printf("Skip linking, because nothing has been updated.\n");
            return FALSE;
        }
        else
        {
            # No compiled file, but there isn't executable file,
            # then linking is required.
            return TRUE;
        }
    }

}

# This function initializes all global variables in this module
sub Makefile_Init
{
    # $targetPath: Path to the target executable file
    # $compiler: Compiler command e.g. 'gcc'
    # $aOption_ref: Reference to the array of the options.
    # $aSourceFiles_ref: Reference to the array which has paths to all the source files
    # $objPath: Path to a folder where all object files are stored
    my ($targetName, $compiler, $aOptions_ref, $aSourceFiles_ref, $aIncludePaths_ref, $objPath) = @_;

    # Save the compiler command into a global variable
    $gCompiler = $compiler;

    # Save the object path into a global variable
    $gObjPath = $objPath;

    # Save the target file path into a global variable
    $gTargetPath = $objPath.'/'.$targetName;

    # Initialize an array which will contains all source, object, dependency file paths.
    # For more explanation, see where this is defined.
    @gaAllRelevantFiles = MakeAllRelevantFileHash($aSourceFiles_ref, $objPath);

    # Initialize option arguments
    $gOptionString = OptionArrayToCommand($aOptions_ref);

    # Initialize include arguments
    $gIncludeString = IncludePathArrayToCommand($aIncludePaths_ref);
}

# This function decides if there is valid executable generated as
# seeing the compilation state and linking state.
sub IsTheExecutableValid
{
    # $compileState: Previous Compilation state
    # $linkState: Previous linking state
    my ($compileState, $linkState) = @_;

    # Check the compilation state
    if ($compileState == AT_LEAST_ONE_COMPILE_ERROR)
    {
        # Compile failed, then no valid executable anyway
        return(EXECUTABLE_INVALID);
    }

    # Check the linking state
    if($linkState == LINK_ERROR)
    {
        # Linking failed, then no valid executable anyway
        return(EXECUTABLE_INVALID);
    }

    # No error, then the execute file is valid
    return(EXECUTABLE_VALID);
}

# This function will make target object executable file. But only out-of-date source files are compiled.
# That is, up-to-data files will be skipped to be compiled.
# Linking is also skipped if all the object files are not updated.
# Then return the compile state.
sub Makefile_Make()
{
    # If not exists, Create a folder where all object files will be stored.
    CreateObjectFolder($gObjPath);

    # Compile all the sources and get the status
    my $compileState = CompileSources($gCompiler, \@gaAllRelevantFiles, $gOptionString, $gIncludeString);

    my $linkState;

    # Check if linking is required
    if(IsLinkingRequiered($gTargetPath, $compileState) == TRUE)
    {
        # If required, then link them
        $linkState = LinkObjects($gCompiler, \@gaAllRelevantFiles, $gOptionString, $gTargetPath);
    }
    else
    {
        $linkState = LINK_SKIPPED;
    }

    return(IsTheExecutableValid($compileState, $linkState));
}

# This function removes all the object/dependency files in the object folder.
# Removes the target executable file as well.
sub Makefile_Clear()
{
    # Get the list of all files in the object path
    my @afiles = glob( $gObjPath . '/*' );

    # Remove all files in the object directly
    foreach my $file (@afiles)
    {
        # Remove a file
        unlink $file;
    }
}

# This function will compile all source files in any cases.
# Then return the compile state.
sub Makefile_Build()
{
    # Removes all the object/dependency files in the object folder.
    Makefile_Clear();

    # Then, make
    return(Makefile_Make());
}

1;
