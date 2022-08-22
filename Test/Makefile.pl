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

sub CompileSources
{
    my ($optionStr, $includeStr) = @_;

    my %FileDependencies = CodeDepandency_GetFileDependency(\@cFileList, \@includePath);

    # Start compiling
    foreach my $src_obj (@src_objFilePath)
    {
        if (-e $src_obj->{obj}) #$src_obj->{obj} exist?
        {
            my $dependList = %FileDependencies{$src_obj->{src}};

            if(IsObjFileLatest($src_obj->{src}, $src_obj->{obj}, $dependList) == $OBJ_IS_OUT_OF_DATE)
            {
                # There are some source files modified. Let's compile.
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
        }

        # Compiling here
        my $cmd = $cCompiler." ".$optionStr." ".$includeStr." -c ".$src_obj->{src}." -o ".$src_obj->{obj};
        printf($cmd."\n");
        system($cmd);
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

sub make()
{
    MakeObjectFilePathArray();

    my $option = OptionArrayToCommand(\@cOption);
    my $include = IncludePathArrayToCommand(\@includePath);

    CreateObjectFolder();

    CompileSources($option, $include);

    BuildTarget($option, $targetName);
}

make();
