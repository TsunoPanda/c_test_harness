package Makefile;
use strict;
use feature 'state';
use lib qw(./);
use Exporter;
our @ISA = qw(Exporter);
our @EXPORT = qw(Makefile_Init Makefile_make Makefile_clear Makefile_rebuild);


my $targetName = "TestProgram.exe";

my $cCompiler = "gcc";

my @cOption = 
(
    "-Wall",
    "-O2",
    "-MMD",
);

my @cFileList =
(
    "../ProductCode/LedDriver/LedDriver.c",
    "../ProductCode/MyMath/MyMath.c",
    "../ProductCode/SetAndGet/SetAndGet.c",
    "./TestCode/LedDriverTest.c",
    "./TestHarness/unity.c",
    "./TestHarness/unity_fixture.c",
    "./TestHarness/unity_memory.c",
    "./TestRunner/LedDriverTestRunner.c",
    "./TestRunner/test_main.c",
);

my @includePath =
(
    "../ProductCode/LedDriver/",
    "../ProductCode/MyMath/",
    "../ProductCode/SetAndGet/",
    "./TestHarness/"
);

my $objPath = "./Obj";

# This is array of hashes. The hashes will have source path (key:src) and object path (key:obj)
my @src_objFilePath = ();


use constant FILE1_IS_NEW   => 0;
use constant FILE2_IS_NEW   => 1;
use constant SAME_TIMESTAMP => 2;

use constant OBJ_IS_OUT_OF_DATE => 0;
use constant OBJ_IS_UP_TO_DATE  => 1;

sub GetTimeStampValueByCheckingFileSystem
{
    my ($file) = @_;

    my @filestat = stat $file;

    my $file_time = $filestat[9];

    return $file_time;
}

sub GetTimeStampValue
{
    my ($file) = @_;

    state %TimeStampList = ();

    if (exists($TimeStampList{$file}))
    {
        # get the value from the hash.
        return $TimeStampList{$file};
    }
    else
    {
        my $file_time = GetTimeStampValueByCheckingFileSystem($file);

        # save the file time
        $TimeStampList{$file} = $file_time;

        return $file_time;
    }
}

sub CompareFileTimestamps
{
    my ($file1, $file2) = @_;

    my $timestameValue1 = GetTimeStampValue($file1);
    my $timestameValue2 = GetTimeStampValue($file2);
    if ($timestameValue1 < $timestameValue2)
    {
        return FILE2_IS_NEW;
    }
    elsif ($timestameValue1 > $timestameValue2)
    {
        return FILE1_IS_NEW;
    }
    else
    {
        return SAME_TIMESTAMP;
    }
}

sub OptionArrayToCommand
{
    my ($ref_optionArray) = @_;

    my $cFlag = "";
    foreach my $i_cFlag (@{$ref_optionArray})
    {
        $cFlag = $cFlag.$i_cFlag." ";
    }
    chop($cFlag);
    return $cFlag;
}

sub IncludePathArrayToCommand
{
    my ($ref_optionArray) = @_;
    my @includeOptions = ();
    foreach my $i_inPath (@{$ref_optionArray})
    {
        push(@includeOptions, "-I ".$i_inPath);
    }

    return OptionArrayToCommand(\@includeOptions);
}

sub MakeObjectFilePathArray()
{
    # Make Object file paths
    foreach my $i_cFile (@cFileList)
    {
        if ($i_cFile =~ /.*(\/.+)\.c/)
        {
            my $src_obj = {'src' => "", 'obj' => ""};
            $src_obj->{'src'} = $i_cFile;
            $src_obj->{'obj'} = $objPath.$1.".o";
            $src_obj->{'dep'} = $objPath.$1.".d";
            push(@src_objFilePath, $src_obj);
        }
        else
        {
            printf("Warning: The way to define the c file is not correct.\n");
            printf(">>> ".$i_cFile."\n");
        }
    }
}

sub CreateObjectFolder
{
    my $objTmp = $objPath;
    $objTmp =~ s/\//\\/g;
    system("if not exist ".$objTmp." mkdir ".$objTmp);
}

sub IsObjFileLatest
{
    my ($src, $obj, $dependList) = @_;
    foreach my $dependFile (@{$dependList})
    {
        if(CompareFileTimestamps($dependFile, $obj) == FILE1_IS_NEW)
        {
            return OBJ_IS_OUT_OF_DATE;
        }
    }
    return OBJ_IS_UP_TO_DATE;
}

my $COMPILE_SUCCEEDED = 0;
my $COMPILE_ERROR     = 1;
sub IssueCompileCommand
{
    my ($cCompiler, $optionStr, $includeStr, $src_obj) = @_;

    # Make compiling command
    my $compile_cmd = $cCompiler." ".$optionStr." ".$includeStr." -c ".$src_obj->{src}." -o ".$src_obj->{obj};

    # Adding '2>&1' means send stderr(2) to the same place as stdout (&1))
    $compile_cmd = $compile_cmd.' 2>&1';

    # Display the command.
    printf($compile_cmd."\n");

    # Execute the command and get the STDOUT using 'qx//' syntax.
    my $output = qx/$compile_cmd/;

    # Display the result.
    printf($output);

    if($output =~ /error/)
    {
        return $COMPILE_ERROR;
    }
    else
    {
        return $COMPILE_SUCCEEDED;
    }
}

my $NO_COMPILED_FILE = 0;
my $NO_COMPILE_ERROR = 1;
my $AT_LEAST_ONE_COMPILE_ERROR = 2;
sub CompileSources
{
    my ($optionStr, $includeStr) = @_;
    
    my $no_compile_error = 0;
    my $at_least_one_compiling_error = 1;
    my $error_state = $no_compile_error;

    my $no_compiled_file = 0;
    my $at_least_one_compiled_file = 1;
    my $compile_state = $no_compiled_file;

    # Start compiling
    foreach my $src_obj (@src_objFilePath)
    {
        #$src_obj->{obj} and $src_obj->{dep} exist?
        if (-e $src_obj->{obj} && -e $src_obj->{dep})
        {
            my @dependList = GetRelatedFileList($src_obj->{dep});

            if(IsObjFileLatest($src_obj->{src}, $src_obj->{obj}, \@dependList) == OBJ_IS_OUT_OF_DATE)
            {
                # There are some source files modified. Let's compile.
                $compile_state = $at_least_one_compiled_file;
                if(IssueCompileCommand($cCompiler, $optionStr, $includeStr, $src_obj) == $COMPILE_ERROR)
                {
                    $error_state = $at_least_one_compiling_error;
                }
            }
            else
            {
                # Source file is not updated. skip.
                printf("skip compiling ".$src_obj->{obj}."\n");
                next;
            }
        }
        else
        {
            # Object file is not exists. Let's compile.
            $compile_state = $at_least_one_compiled_file;
            if(IssueCompileCommand($cCompiler, $optionStr, $includeStr, $src_obj) == $COMPILE_ERROR)
            {
                $error_state = $at_least_one_compiling_error;
            }
        }
    }

    if($compile_state == $no_compiled_file)
    {
        return $NO_COMPILED_FILE;
    }
    else
    {
        if($error_state == $no_compile_error)
        {
            return $NO_COMPILE_ERROR
        }
        else
        {
            return $AT_LEAST_ONE_COMPILE_ERROR
        }
    }
}

sub BuildTarget
{
    my ($optionStr, $targetStr) = @_;

    my $objectsStr = "";
    foreach my $src_obj (@src_objFilePath)
    {
        $objectsStr = $objectsStr.$src_obj->{'obj'}." "
    }

    my $cmd = $cCompiler." ".$optionStr." -o ".$targetStr." ".$objectsStr;

    printf($cmd."\n");
    system($cmd);
}

sub GetRelatedFileList
{
    my ($dFilePath) = @_;

    my @fileList = ();

    # Open the target text file.
    open(InFile, "< ".$dFilePath) or die("Can't open the dependency file.");

    # Read the file line by line.
    while (my $line = <InFile>)
    {
        # clean the line string
        $line =~ s/.+\://g; # Remove the object file
        $line =~ s/\\//g; # Remove '/'
        $line =~ s/^ //g; # Remove a space at the top.

        # If the line contains '#include "xxxx"' ?
        push(@fileList, split(/\s+/, $line));
    }

    # Close the target text file.
    close(InFile);

    return @fileList;
}

my $option = "";
my $include = "";
sub Makefile_Init()
{
    MakeObjectFilePathArray();

    $option = OptionArrayToCommand(\@cOption);
    $include = IncludePathArrayToCommand(\@includePath);
}

sub Makefile_make()
{
    CreateObjectFolder();

    my $compile_state = CompileSources($option, $include);
    if($compile_state == $NO_COMPILED_FILE)
    {
        if(-e './'.$targetName)
        {
            printf("Skip linking, because nothing has been updated.\n");
        }
        else
        {
            BuildTarget($option, $targetName);
        }
    }
    elsif($compile_state == $NO_COMPILE_ERROR)
    {
        BuildTarget($option, $targetName);
    }
    else # $compile_state = $AT_LEAST_ONE_COMPILE_ERROR
    {
        printf("Skip linking, because at least one compile error happened.\n");
    }
}

sub Makefile_clear()
{
    foreach my $hash_src_obj (@src_objFilePath)
    {
        unlink $hash_src_obj->{obj};
    }
    unlink $targetName;
}

sub Makefile_rebuild()
{
    Makefile_clear();
    Makefile_make();
}

1;
