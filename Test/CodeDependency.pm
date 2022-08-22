package CodeDependency;
use strict;
use feature 'state';

### This is an idea that saving the file dependency map into the disk. ###
### But it turned out that it is much slower than analyzing all text file. ###
#use DBM::Deep;
#tie(my %FileDependencyMap, "DBM::Deep", "depend.db");

my %FileDependencyMap = ();

my @AllFiles = ();

use lib qw(./);
use Exporter;
our @ISA = qw(Exporter);
our @EXPORT = qw(CodeDepandency_GetFileDependency);


my $FIRST_TIME_TRUE = 0;
my $FIRST_TIME_FALSE = 1;

sub SearchIncludePath
{
    my ($incFile, $incPaths) = @_;

    foreach my $incPath (@{$incPaths})
    {
        if (-e $incPath.$incFile)
        {
            return $incPath.$incFile;
        }
    }
}

sub GetPathArrayByAnalyzingFileText
{
    my ($filePath, $incPaths, $includePathArray) = @_;

    # Initialize input array.
    @{$includePathArray} = ();

    open(InFile, "< ".$filePath) or die("Can't open the source file.");
    while (my $line = <InFile>)
    {
        if ($line =~ /#[ \t]*include[ \t]*\"(.+)\"/)
        {
            my $includeFile = $1;
            my $fullIncPath = SearchIncludePath($includeFile, $incPaths);
            if ($fullIncPath ne "")
            {
                push(@{$includePathArray}, $fullIncPath);
            }
        }
    }
    close(InFile);
}

sub MakeFileDependencyMap
{
    my ($filePath, $incPaths) = @_;

    my $includePathArray = [];
    GetPathArrayByAnalyzingFileText($filePath, $incPaths, $includePathArray);
    $FileDependencyMap{$filePath} = $includePathArray;
}

sub SearchAndSaveIncludeFiles
{
    my ($pathList) = @_;

    foreach my $incPath (@{$pathList})
    {
        opendir(DIRHANDLE, $incPath);

        foreach my $file (readdir(DIRHANDLE))
        {
            my $filePath = $incPath.$file;

            # if the file is text file
            if (-T $filePath)
            {
                # make entry
                push(@AllFiles, $filePath);
            }
        }

        closedir(DIRHANDLE);
    }
}

sub InputFiles
{
    my ($fileList) = @_;

    foreach my $file (@{$fileList})
    {
        my $false = 0;
        # make entry
        push(@AllFiles, $file);
    }
}

sub MakeFileDependency
{
    state %GetDependTrace = ();

    my ($filePath, $firstTime, $dependingFiles) = @_;

    if ($firstTime == $FIRST_TIME_TRUE)
    {
        @{$dependingFiles} = ();
        %GetDependTrace = ();
    }

    # Remember input file to avoid infinite loop
    $GetDependTrace{$filePath} = "";

    push(@{$dependingFiles}, $filePath);

    foreach my $dependedFile (@{$FileDependencyMap{$filePath}})
    {
        # If it is already exists, skip it to avoid infinite loop
        if (!exists($GetDependTrace{$dependedFile}))
        {
            MakeFileDependency($dependedFile, $FIRST_TIME_FALSE, $dependingFiles);
        }
    }
}

sub CodeDepandency_GetFileDependency
{
    my ($fileList, $pathList) = @_;

    my %FileDependencies = ();

    InputFiles($fileList);

    SearchAndSaveIncludeFiles($pathList);

    foreach my $filePath (@AllFiles)
    {
        MakeFileDependencyMap($filePath, $pathList);
    }

    foreach my $cfile (@{$fileList})
    {
        my $dependList = [];
        MakeFileDependency($cfile, $FIRST_TIME_TRUE, $dependList);
        $FileDependencies{$cfile} = $dependList;
    }

    return %FileDependencies;
}

1;

