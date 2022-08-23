use strict;
use lib qw(./);
use CodeDependency;
use TimeStampComp;

my $targetName = "TestProgram.exe";

my $cCompiler = "gcc";

my @cOption = 
(
    "-Wall",
    "-O2",
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
my @src_objFilePath = ();

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

my $OBJ_IS_OUT_OF_DATE = 0;
my $OBJ_IS_UP_TO_DATE  = 1;
sub IsObjFileLatest
{
    my ($src, $obj, $dependList) = @_;
    foreach my $dependFile (@{$dependList})
    {
        if(TimeStampComp_CompareFiles($dependFile, $obj) == $TimeStampComp::FILE1_IS_NEW)
        {
            return $OBJ_IS_OUT_OF_DATE;
        }
    }
    return $OBJ_IS_UP_TO_DATE;
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

my $NO_COMPILE_ERROR = 0;
my $AT_LEAST_ONE_COMPILE_ERROR = 1;
sub CompileSources
{
    my ($optionStr, $includeStr) = @_;
    my %FileDependencies = CodeDepandency_GetFileDependency(\@cFileList, \@includePath);
    
    my $state = $NO_COMPILE_ERROR;

    # Start compiling
    foreach my $src_obj (@src_objFilePath)
    {
        if (-e $src_obj->{obj}) #$src_obj->{obj} exist?
        {
            my $dependList = %FileDependencies{$src_obj->{src}};

            if(IsObjFileLatest($src_obj->{src}, $src_obj->{obj}, $dependList) == $OBJ_IS_OUT_OF_DATE)
            {
                # There are some source files modified. Let's compile.
                if(IssueCompileCommand($cCompiler, $optionStr, $includeStr, $src_obj) == $COMPILE_ERROR)
                {
                    $state = $AT_LEAST_ONE_COMPILE_ERROR;
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
                if(IssueCompileCommand($cCompiler, $optionStr, $includeStr, $src_obj) == $COMPILE_ERROR)
                {
                    $state = $AT_LEAST_ONE_COMPILE_ERROR;
                }
        }
    }

    return $state;
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

sub make()
{
    MakeObjectFilePathArray();

    my $option = OptionArrayToCommand(\@cOption);
    my $include = IncludePathArrayToCommand(\@includePath);

    CreateObjectFolder();

    if(CompileSources($option, $include) == $NO_COMPILE_ERROR)
    {
        BuildTarget($option, $targetName);
    }
    else
    {
        printf("Skip linking, because at least one compile error happened.\n");
    }
}

make();
