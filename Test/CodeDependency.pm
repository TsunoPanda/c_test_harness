package CodeDependency;
use strict;
use feature 'state';

### This is an idea that saving the file dependency map into the disk. ###
### But it turned out that it is much slower than analyzing all text file. ###
#use DBM::Deep;
#tie(my %ghFileDependencyMap, "DBM::Deep", "depend.db");

# Codes required for exporting this file as a module.
use lib qw(./);
use Exporter;
our @ISA = qw(Exporter);
our @EXPORT = qw(CodeDepandency_GetFileRelationMap);

# Second Input of MakeFileDependency
# Enumeration: $FIRST_TIME_TRUE: MakeFileDependency was called first time.
#              $FIRST_TIME_FALSE: MakeFileDependency was called recursively.
my $gFIRST_TIME_TRUE  = 0;
my $gFIRST_TIME_FALSE = 1;

# This returns full path of the input file as the first parameter "$incFile"
# by searching in the include folder locations input as the second parameter "$aIncPaths".
# It returns "" if no file found.
sub GetFullPath
{
    # $incFile: An include file to be searched for the folders.
    # $aIncPaths: Include paths where this function searched for the file.
    my ($incFile, $aIncPaths) = @_;

    # Search inside all the input include path for the input file name.
    foreach my $incPath (@{$aIncPaths})
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

# This function searches for the text files inside the folders which was input.
# And stores the full path of the found files into a global variable.
sub PushTextFilesUnderIncludePaths
{
    # $aAllFiles: Reference to an array to be contains all source file paths.
    # $aPathList: Folder paths where this function will search for the text file.
    my ($aAllFiles, $aPathList) = @_;

    # Searching into every file paths
    foreach my $incPath (@{$aPathList})
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
                push(@{$aAllFiles}, $filePath);
            }
        }

        # close the folder
        closedir(DIRHANDLE);
    }
}

sub GetListOfSourceFiles
{
    # $aAllFiles: Reference to an array to be contains all source file paths.
    # $aPathList: Folder paths where this function will search for the text file.
    my ($aFileList, $aPathList) = @_;

    # Define and initialize output array.
    my @aAllSourceFiles = ();

    # Push input source files to the array
    push(@aAllSourceFiles, @{$aFileList});

    # Search for the text files inside the input folders
    # And stores the path of the found text files into the array
    PushTextFilesUnderIncludePaths(\@aAllSourceFiles, $aPathList);

    # Return the result
    return @aAllSourceFiles;
}

# This function search for line which contains a C preprocessor  command '#include "xxxx"'
# inside the input text file at the one of the input include folders.
# And it returns the all name of included files as an array.
sub MakeDirectlyRelatedFilePathArray
{
    # $filePath: A source file to be searched into.
    # $aIncPaths: Include folders to be searched for the input text file.
    # $aIncludePathArray: Reference to the array which will contains the list of the included files.
    my ($filePath, $aIncPaths, $aIncludePathArray) = @_;

    # Initialize the input array.
    @{$aIncludePathArray} = ();

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
            my $fullIncPath = GetFullPath($includeFile, $aIncPaths);

            # Found the path of the file?
            if ($fullIncPath ne "")
            {
                # Store the path into the array
                push(@{$aIncludePathArray}, $fullIncPath);
            }
        }
    }

    # Close the target text file.
    close(InFile);
}

sub GetDirectRelationMap
{
    # $filePaths: 
    # $aIncPaths: Include paths where this function will search for the input file.
    my ($afilePaths, $aIncPaths) = @_;

    # Define and initialize output hash
    my %hDirectRekationMap = ();

    foreach my $filePath (@{$afilePaths})
    {
        # Create anonymous array to contain the all related files.
        my $aIncludePathArray = [];

        # Get the all related files and save them into the anonymous array.
        MakeDirectlyRelatedFilePathArray($filePath, $aIncPaths, $aIncludePathArray);

        # Assign the file name as a key. and the value is the reference of the anonymous array.
        $hDirectRekationMap{$filePath} = $aIncludePathArray;
    }

    # Return the result
    return %hDirectRekationMap;
}

# This function creates related file list for every source files as an "array"
# by recursively searching into the input relation map which contains
# information of directly related files of all source files.
# Note: This function is recursive function.
sub MakeRelatedFilePathArray
{
    # $filePath: Related file to be stored into the array
    # $hDirectRelationMap: Reference to the included file map.
    # $aRelatingFiles: Reference to the array where the result will be saved
    # $firstTime: Input $FIRST_TIME_TRUE or nothing when calling this function in other functions.
    #             Input $FIRST_TIME_FALSE when calling this function in this function.
    my ($filePath, $hDirectRelationMap, $aRelatingFiles, $firstTime) = @_;

    # Hash to be used for avoiding duplication of the result and avoid infinite loop.
    # (e.g. headerA.h -> headerB.h -> headerA.h -->....)
    state %hGetDependTrace = ();

    # Counter for recursive call of this function for a safety.
    state $CallCounter = 0;

    # If NOT $firstTime is defined
    unless (defined $firstTime)
    {
        # Assumed it is the first time
        $firstTime = $gFIRST_TIME_TRUE;
    }

    # If it is the first time, then initialize all static variables.
    if ($firstTime == $gFIRST_TIME_TRUE)
    {
        # Initialize the result array.
        @{$aRelatingFiles} = ();

        # Initialize the hash for avoiding duplication and loop
        %hGetDependTrace = ();

        # Initialize the call counter.
        $CallCounter = 0;
    }

    # Increment the call counter
    $CallCounter += 1;

    # If the counter is too large, it is assumed something is wrong.
    if($CallCounter > 1000)
    {
        # Display message
        printf("Too long recursive call of AddFileRelationToTheMap in CodeDependency module.\n");

        # abort this program
        exit(1);
    }

    # Remember input file to avoid duplication and infinite loop
    $hGetDependTrace{$filePath} = "";

    # Push the file path into the result array
    push(@{$aRelatingFiles}, $filePath);

    # Check the all related files of the input file.
    foreach my $dependedFile (@{$hDirectRelationMap->{$filePath}})
    {
        # If it has been already checked, skip it to avoid infinite loop
        if (!exists($hGetDependTrace{$dependedFile}))
        {
            # Get all related files of the related files of the input file.
            MakeRelatedFilePathArray($dependedFile, $hDirectRelationMap, $aRelatingFiles, $gFIRST_TIME_FALSE);
        }
    }
}

sub GetRelationMap
{
    # $aCfilePaths: Related file to be stored into the array
    # $hDirectRelationMap: Reference to the included file map.
    my ($aCfilePaths, $hDirectRelationMap) = @_;

    # Define and initialize output hash
    my %hRelationMap = ();

    # Create the file relation map for all input source files.
    foreach my $cfile (@{$aCfilePaths})
    {
        # Create Anonymous array of the relation files of a source file
        my $aRelatingList = [];

        # Get the relation map of the source file.
        MakeRelatedFilePathArray($cfile, $hDirectRelationMap, $aRelatingList);

        # Save the reference of the relation map with key of the file name.
        $hRelationMap{$cfile} = $aRelatingList;
    }

    # Return the result
    return %hRelationMap;
}

# This function returns a hash.
# The key of the hash is path of all source files input as the first parameter.
# And the value related to a key is a reference to the array
# that contains paths to the all files related to the key file.
# The related files are searched into the path lists input as the second parameter.
sub CodeDepandency_GetFileRelationMap
{
    # $aFileList: list of the source files. Related file lists of these files are generated.
    # $aPathList: list of the paths where related files are searched.
    my ($aFileList, $aPathList) = @_;

    # This array contains all source file path.
    my @aAllSourceFiles = GetListOfSourceFiles($aFileList, $aPathList);

    # This will contain all source file path as a key. 
    # And the key points an array which contains all files included by the key file.
    my %hDirectRelationMap = GetDirectRelationMap(\@aAllSourceFiles, $aPathList);;

    # This hash is the file relation map having the information all related files
    # for all .c files.
    my %hRelationMap = GetRelationMap($aFileList, \%hDirectRelationMap);

    # Return the relation map
    return %hRelationMap;
}

1;

