package CheckDependency;

use lib qw(./);
use Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(CheckDepandency_GetFileDependency CheckDepandency_IsObjFileLatest);

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

sub CheckDepandency_GetFileDependency
{
    my ($fileList, $pathList) = @_;

    %FileDependencyMap = ();
    %FileDependencies = ();

    InputFiles($fileList);

    SearchAndSaveIncludeFiles($pathList);

    foreach my $filePath (keys(%FileDependencyMap))
    {
        MakeFileDependencyMap($filePath, $pathList);
    }

    foreach my $cfile (@{$fileList})
    {
        my $dependList = [];
        GetDependency($cfile, $FIRST_TIME_TRUE, $dependList);
        $FileDependencies{$cfile} = $dependList;

    }

    return %FileDependencies;
}

1;

