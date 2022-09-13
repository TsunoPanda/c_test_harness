package TimeStampComp;
use strict;
use feature 'state';
use lib qw(./);
use Exporter;
our @ISA = qw(Exporter);
our @EXPORT = qw(TimeStampComp_CompareFiles TimeStampComp_IsTheFileLatest);
our @EXPORT_OK = ('FILE1_IS_NEWER', 'FILE2_IS_NEWER', 'SAME_TIMESTAMP');

###############################################
####### Definitions of Constant values ########
###############################################
# Generic used value. false and true
use constant FALSE => (1==0);
use constant TRUE  => (0==0);

# Return value of 'CompareFileTimestamps'
use constant FILE1_IS_NEWER   => 0;
use constant FILE2_IS_NEWER   => 1;
use constant SAME_TIMESTAMP => 2;

# Initialize time stamp list. For more explanation, see where this is defined.
# This hash will have the file paths as keys, and the value will be the time stamp value of the file.
# That is, the time stamp value of the file will be saved in this hash not to call system
# function every time to check the time stamp value.
our %ghSavedTimeStampList = ();

# This function returns comparable time stamp value of the input file.
sub GetTimeStampValueByCheckingFileSystem
{
    # $file: The input file path
    my ($file) = @_;

    # Get the status of the file
    my @filestat = stat $file;

    # Get the last modified time of the file
    use constant LAST_MODIFIED_TIME => 9;
    my $file_time = $filestat[LAST_MODIFIED_TIME];

    # Return the value
    return $file_time;
}

# This function returns the time stamp value of the input file.
# If the '%ghSavedTimeStampList' has the time stamp value of the input file,
# it returns from the hash. Unless, it will check the system file stamp value.
sub GetTimeStampValue
{
    # $file: The input file path
    my ($file) = @_;

    # Has the time stamp value of the file been stored?
    if (exists($ghSavedTimeStampList{$file}))
    {
        # Return the value from the hash.
        return $ghSavedTimeStampList{$file};
    }
    else
    {
        # Get the value from the system
        my $file_time = GetTimeStampValueByCheckingFileSystem($file);

        # Save the file time to the hash.
        $ghSavedTimeStampList{$file} = $file_time;

        # Return the value
        return $file_time;
    }
}

# This function compares the time stamps of the input files.
# Returns 'FILE1_IS_NEW', if the time stamp value of the file in the first input is larger.
# Returns 'FILE2_IS_NEW', if the time stamp value of the file in the second input is larger.
# Returns 'SAME_TIMESTAMP', if the time stamp value of the two files are the same.
sub TimeStampComp_CompareFiles
{
    # $file1: The input file path of the first input
    # $file2: The input file path of the second input
    my ($file1, $file2) = @_;

    # Get the time stamp value of the first input file.
    my $timestameValue1 = GetTimeStampValue($file1);

    # Get the time stamp value of the second input file.
    my $timestameValue2 = GetTimeStampValue($file2);

    # If the time stamp value of the second input file is larger...
    if ($timestameValue1 < $timestameValue2)
    {
        # The second input file is newer.
        return FILE2_IS_NEWER;
    }
    # If the time stamp value of the first input file is larger...
    elsif ($timestameValue1 > $timestameValue2)
    {
        # The first input file is newer.
        return FILE1_IS_NEWER;
    }
    else
    {
        # Else, they have the same time stamp value.
        return SAME_TIMESTAMP;
    }
}

# This function checks if the first input file is the latest compared to 
# the files in the list input as the second parameter.
sub TimeStampComp_IsTheFileLatest
{
    # $inFile: The file to be checked.
    # $aFileList_ref: Reference to the array containing files to be compared.
    my ($inFile, $aFileList_ref) = @_;

    # Check the file with all files in the array
    foreach my $fileCompared (@{$aFileList_ref})
    {
        # If a file in the array is newer,
        if(TimeStampComp_CompareFiles($inFile, $fileCompared) == FILE2_IS_NEWER)
        {
            # Return false
            return FALSE;
        }
    }

    # Reaching here means the checked file is the newest one.
    return TRUE;
}

1;
