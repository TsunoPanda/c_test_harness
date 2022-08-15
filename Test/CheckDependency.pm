package CheckDependency;

use lib qw(./);
use TimeStampComp;
use Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(CheckDepandency_Init CheckDepandency_IsObjFileLatest);

use Data::Dumper;

our $OBJ_IS_OUT_OF_DATE = 0;
our $OBJ_IS_UP_TO_DATE  = 1;
our %FileDependencyMap;

my $FIRST_TIME_TRUE = 0;
my $FIRST_TIME_FALSE = 1;

my %GetDependTrace = ();

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

sub MakeFileDependencyMap
{
    my ($filePath, $incPaths) = @_;

    my $includePathArray = [];

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
                $FileDependencyMap{$filePath} = "";
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
        # make entry
        $FileDependencyMap{$file} = "";
    }
}

sub GetDependency
{
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
            GetDependency($dependedFile, $FIRST_TIME_FALSE, $dependingFiles);
        }
    }
}

sub CheckDepandency_Init
{
    my ($fileList, $pathList) = @_;

    InputFiles($fileList);

    SearchAndSaveIncludeFiles($pathList);

    foreach my $filePath (keys(%FileDependencyMap))
    {
        MakeFileDependencyMap($filePath, $pathList);
    }
}

sub CheckDepandency_IsObjFileLatest
{
    my ($src, $obj) = @_;
    my @dependList;

    GetDependency($src, $FIRST_TIME_TRUE, \@dependList);
    foreach my $dependFile (@dependList)
    {
        if(TimeStampComp_CompareFiles($dependFile, $obj) == $TimeStampComp::FILE1_IS_NEW)
        {
            return $OBJ_IS_OUT_OF_DATE;
        }
    }
    return $OBJ_IS_UP_TO_DATE;
}

1;

