package CodeDependency;
use strict;
use feature 'state';

### This is an idea that saving the file dependency map into the disk. ###
### But it turned out that it is much slower than analyzing all text file. ###
#use DBM::Deep;
#tie(my %FileDependencyMap, "DBM::Deep", "depend.db");

# This will contain all source file path as a key. 
# And the key points an array which contains all files included by the key file.
my %FileDependencyMap = ();

# This array will contain all source file path.
my @AllFiles = ();

# Codes required for exporting this file as a module.
use lib qw(./);
use Exporter;
our @ISA = qw(Exporter);
our @EXPORT = qw(CodeDepandency_GetFileDependency);

# Second Input of MakeFileDependency
# Enumeration: $FIRST_TIME_TRUE: MakeFileDependency was called first time.
#              $FIRST_TIME_FALSE: MakeFileDependency was called recursively.
my $FIRST_TIME_TRUE  = 0;
my $FIRST_TIME_FALSE = 1;

# This returns full path of the input file as the first parameter "$incFile"
# by searching in the include folder locations input as the second parameter "$incPaths"
# It returns "" if no file found.
sub SearchIncludePath
{
    # $incFile: An include file to be searched for the folders.
    # $incPaths: Include paths where this function searched for the file.
    my ($incFile, $incPaths) = @_;

    # Search inside all the input include path for the input file name.
    foreach my $incPath (@{$incPaths})
    {
        # Exists the file?
        if (-e $incPath.$incFile)
        {
            # Return the full path of the file.
            return $incPath.$incFile;
        }
    }

    # No file found, Return ""
    return "";
}

# This function search for line which contains a C preprocessor  command '#include "xxxx"'
# inside the input text file at the one of the input include folders.
# And it returns the all name of included files as an array.
sub GetPathArrayByAnalyzingFileText
{
    # $filePath: A source file to be searched into.
    # $incPaths: Include folders to be searched for the input text file.
    # $$includePathArray: Reference to the array which will contains the list of the included files.
    my ($filePath, $incPaths, $includePathArray) = @_;

    # Initialize the input array.
    @{$includePathArray} = ();

    # Open the target text file.
    open(InFile, "< ".$filePath) or die("Can't open the source file.");

    # Read the file line by line.
    while (my $line = <InFile>)
    {
        # If the line contains '#include "xxxx"' ?
        if ($line =~ /#[ \t]*include[ \t]*\"(.+)\"/)
        {
            # Capture the included file name
            my $includeFile = $1;

            # Get full path of the included file.
            my $fullIncPath = SearchIncludePath($includeFile, $incPaths);

            # Found the path of the file?
            if ($fullIncPath ne "")
            {
                # Store the path into the array
                push(@{$includePathArray}, $fullIncPath);
            }
        }
    }

    # Close the target text file.
    close(InFile);
}

# This function creates the contents of global variable %FileDependencyMap.
# This will search the inside of the text source files.
sub MakeFileDependencyMap
{
    # $filePath: A source file path. The list of the included files by this source file will be created.
    # $incPaths: Include paths where this function will search for the input file.
    my ($filePath, $incPaths) = @_;

    # Create anonymous array to contain the all related files.
    my $includePathArray = [];

    # Get the all related files and save them into the anonymous array.
    GetPathArrayByAnalyzingFileText($filePath, $incPaths, $includePathArray);

    # Assign the file name as a key. and the value is the reference of the anonymous array.
    $FileDependencyMap{$filePath} = $includePathArray;
}

# This function searches for the text files inside the folders which was input.
# And stores the full path of the found files into a global variable.
sub SearchAndSaveIncludeFiles
{
    # $PathList: Folder paths where this function will search for the text file.
    my ($pathList) = @_;

    # Searching into every file paths
    foreach my $incPath (@{$pathList})
    {
        # Open the folder included the input list.
        opendir(DIRHANDLE, $incPath);

        # Checking all files included by the folder.
        foreach my $file (readdir(DIRHANDLE))
        {
            # Get full path of the file.
            my $filePath = $incPath.$file;

            # Is the file a text file?
            if (-T $filePath)
            {
                # Save it into a global variable
                push(@AllFiles, $filePath);
            }
        }

        # close the folder
        closedir(DIRHANDLE);
    }
}

# This function creates related file list for every source files as an "array"
# by recursively searching into a global variable %FileDependencyMap which contains
# information of direct related files of every files.
# Note: This function is recursive function.
sub MakeFileDependency
{
    # $filePath: Related file to be stored into the array
    # $dependingFiles: Reference to the array where the result will be saved
    # $firstTime: Input $FIRST_TIME_TRUE or nothing when calling this function in other functions.
    #             Input $FIRST_TIME_FALSE when calling this function in this function.
    my ($filePath, $dependingFiles, $firstTime) = @_;

    # Hash to be used for avoiding duplication of the result and avoid infinite loop.
    # (e.g. headerA.h -> headerB.h -> headerA.h -->....)
    state %GetDependTrace = ();

    # Counter for recursive call of this function for a safety.
    state $CallCounter = 0;

    # If NOT $firstTime is defined
    unless (defined $firstTime)
    {
        # Assumed it is the first time
        $firstTime = $FIRST_TIME_TRUE;
    }

    # If it is the first time, then initialize all static variables.
    if ($firstTime == $FIRST_TIME_TRUE)
    {
        # Initialize the result array.
        @{$dependingFiles} = ();

        # Initialize the hash for avoiding duplication and loop
        %GetDependTrace = ();

        # Initialize the call counter.
        $CallCounter = 0;
    }

    # Increment the call counter
    $CallCounter += 1;

    # If the counter is too large, it is assumed something is wrong.
    if($CallCounter > 1000)
    {
        # Display message
        printf("Too long recursive call of MakeFileDependency in CodeDependency module.\n");

        # abort this program
        exit(1);
    }

    # Remember input file to avoid duplication and infinite loop
    $GetDependTrace{$filePath} = "";

    # Push the file path into the result array
    push(@{$dependingFiles}, $filePath);

    # Check the all related files of the input file.
    foreach my $dependedFile (@{$FileDependencyMap{$filePath}})
    {
        # If it has been already checked, skip it to avoid infinite loop
        if (!exists($GetDependTrace{$dependedFile}))
        {
            # Get all related files of the related files of the input file.
            MakeFileDependency($dependedFile, $dependingFiles, $FIRST_TIME_FALSE);
        }
    }

}

# This function returns a hash.
# The key of the hash is path of all source files input as the first parameter.
# And the value related to a key is a reference to the array
# that contains paths to the all files related to the key file.
# The related files are searched into the path lists input as the second parameter.
sub CodeDepandency_GetFileDependency
{
    # $fileList: list of the source files. Related file lists of these files are generated.
    # $pathList: list of the paths where related files are searched.
    my ($fileList, $pathList) = @_;

    # Define the result hash to be output
    my %FileDependencies = ();

    # Push input files global array
    push(@AllFiles, @{$fileList});

    # Search for the text files inside the input folders
    # And stores the path of the found text files into a global variable.
    SearchAndSaveIncludeFiles($pathList);

    # Create file dependency map by checking all files
    foreach my $filePath (@AllFiles)
    {
        # Creates the contents of make file dependency map by searching all path list.
        MakeFileDependencyMap($filePath, $pathList);
    }

    # Create file relation array for all input source files.
    foreach my $cfile (@{$fileList})
    {
        # Anonymous array of the related files
        my $dependList = [];

        # Get the related files.
        MakeFileDependency($cfile, $dependList);

        # Save the reference of the anonymous array into the hash to be output.
        $FileDependencies{$cfile} = $dependList;
    }

    # Return the hash
    return %FileDependencies;
}

1;

