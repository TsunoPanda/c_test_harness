use strict;
use Data::Dumper;

use lib qw(./);
use CheckDependency;

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
    foreach my $i_inPath (@{$ref_optionArray})
    {
        $i_inPath = "-I ".$i_inPath;
    }

    return OptionArrayToCommand($ref_optionArray);
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


sub CompileSources
{
    my ($optionStr, $includeStr) = @_;

    # Start compiling
    foreach my $src_obj (@src_objFilePath)
    {
        if (-e $src_obj->{obj}) #$src_obj->{obj} exist?
        {
            if(CheckDepandency_IsObjFileLatest($src_obj->{src}, $src_obj->{obj}) == $CheckDependency::OBJ_IS_OUT_OF_DATE)
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

    CheckDepandency_Init(\@cFileList, \@includePath);

    my $option = OptionArrayToCommand(\@cOption);
    my $include = IncludePathArrayToCommand(\@includePath);

    CreateObjectFolder();

    CompileSources($option, $include);

    BuildTarget($option, $targetName);
}

make();
