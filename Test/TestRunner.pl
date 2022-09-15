use strict;
use lib qw(./);
use Makefile;
use Makefile 'EXECUTABLE_VALID';
use TimeStampComp;

use Time::HiRes qw( usleep gettimeofday tv_interval );

############################################
##### Global Configuration Parameters ######
############################################
# The compiler command
my $gCompiler = '';

# Compiler options for Test harness codes
my @gaHarnessOptions = ();

# Test Harness source files
my @gaHarnessSrcFiles = ();

# Compiler options for Test code
my @gaTestCodeOptions = ();

# Test code files
my @gaTestSrcFiles = ();

# Compiler options for Test code
my @gaProductCodeOptions = ();

# Product code files
my @gaProductSrcFiles = ();

# Linker option
my @gaLinkerOptions = ();

# Include paths
my @gaIncludePaths = ();

use constant TEST_CODE_PATH      => 'TestCode';
use constant HARNESS_CODE_PATH   => 'TestHarness';
use constant LOCAL_CONFIG_FILE   => 'MakeConfig.pl';
use constant HARNESS_CONFIG_FILE => 'MakeConfig.pl';

### End of Global Configuration Parameters ###

# Test module name from the first command line argument
our $TestModule;

# Test run type from the second command line argument
our $RunType;

# Folder which has test codes, make configuration file to be executed
our $testModuleFolder;

# Folder where compilation result to be stored
our $gTestObjPath;

# Folder where compilation result of test harness code to be stored
our $gHarnessObjPath;

# The executable file name to be generated
our $gTargetPath;

# Generic used value. false and true
use constant FALSE => (1==0);
use constant TRUE  => (0==0);

sub GetHarnessConfigPath
{
    # Make the global make configuration file path
    my $harnessConfigPath = './'.HARNESS_CODE_PATH.'/'.HARNESS_CONFIG_FILE;

    # The configuration file exist?
    unless(-e $harnessConfigPath)
    {
        # It did not exist.
        printf("Could not find the ".LOCAL_CONFIG_FILE." in the same folder with this script.\n");
        exit(1);
    }

    return($harnessConfigPath);
}

sub GetTheTestConfigPath
{
    # Make the local make configuration file path
    my $testConfigPath = './'.TEST_CODE_PATH.'/'.$TestModule.'/'.LOCAL_CONFIG_FILE;

    # The configuration file exist?
    unless(-e $testConfigPath)
    {
        # It did not exist.
        printf("Could not find the ".LOCAL_CONFIG_FILE." in the test module folder\n");
        exit(1);
    }

    # Save the local configuration parameter
    return($testConfigPath);
}

sub RemoveObjIfTheConfigFilesUpToDate
{
    # Make the local make configuration file path
    my $testConfigPath = GetTheTestConfigPath();

    my @testObjfiles = glob( $gTestObjPath . '/*.o' );

    if(@testObjfiles != 0)
    {
        if (TimeStampComp_IsTheFileLatest($testConfigPath, \@testObjfiles) == TRUE)
        {
            printf("!!!Test configuration file was updated. Remove Local objects!!!\n");
            for my $testObjfile (@testObjfiles)
            {
                unlink $testObjfile;
            }
        }
    }

    # Make the global make configuration file path
    my $harnessConfigPath = GetHarnessConfigPath();

    my @harnessObjfiles = glob( $gHarnessObjPath . '/*.o' );

    if(@harnessObjfiles != 0)
    {
        if (TimeStampComp_IsTheFileLatest($harnessConfigPath, \@harnessObjfiles) == TRUE)
        {
            printf("!!!Harness configuration file was updated. Remove Local objects!!!\n");
            for my $harnessObjfile (@harnessObjfiles)
            {
                unlink $harnessObjfile;
            }
        }
    }
}

# This function will get command line arguments,
# and initializes global variables according to them
sub InitializeGlobalVariablesFromCommandLineArguments
{
    # Check the number of input command line arguments.
    if (@ARGV < 1)
    {
        # No arguments. Then, exit with messages
        printf("Please input the test module as the first parameter.\n");
        exit(1);
    }
    elsif(@ARGV <2)
    {
        # One arguments. Get test module name from the first parameter.
        $TestModule = $ARGV[0];

        # Assume the second parameter is 'Make'
        $RunType    = 'Make';
    }
    else
    {
        # Two arguments.
        # Get test module name from the first parameter.
        $TestModule = $ARGV[0];

        # Get run type from the second parameter.
        $RunType    = $ARGV[1];
    }

    # Make path of the test module
    $testModuleFolder = './'.TEST_CODE_PATH.'/'.$TestModule;

    # Make target executable file name
    $gTargetPath = $testModuleFolder.'/Obj/'.$TestModule.'Test.exe';

    # Make folder path where the object files are saved
    $gTestObjPath = $testModuleFolder.'/Obj';

    $gHarnessObjPath = './'.HARNESS_CODE_PATH.'/Obj';
}

# This function checks if the test module folder exists,
# if it does not exists, stops this program with messages.
sub CheckExistenceOfTheTestModule
{
    # The test module folder exist?
    unless(-d $testModuleFolder)
    {
        # It did not exist. exit with message.
        printf("Could not find the test module folder\n");
        exit(1);
    }
}

# This function reads global make configuration file, and 
# saves them into global variables
sub SaveHarnessConfiguration
{
    # Path to the global make configuration file
    my $harnessConfigPath = GetHarnessConfigPath();

    # Fetch the local configuration
    my %HarnessConfig = do $harnessConfigPath;

    # Save the compiler command
    $gCompiler = $HarnessConfig{'Compiler'};

    # Append local options to global configuration parameter
    push(@gaHarnessOptions, @{$HarnessConfig{'HarnessOptions'}});

    # Append local source files to be compiled to global configuration parameter
    push(@gaHarnessSrcFiles, @{$HarnessConfig{'HarnessSourceFiles'}});

    # Append local include paths to global configuration parameter
    push(@gaIncludePaths, @{$HarnessConfig{'IncludePaths'}});
}

# This function reads local make configuration file, and 
# saves them into global variables
sub SaveTestConfiguration
{
    # Path to the make configuration file of the test module
    my $testConfigPath = GetTheTestConfigPath();

    # Fetch the local configuration
    my %testConfig = do $testConfigPath;

    # Append local options to global configuration parameter
    push(@gaTestCodeOptions, @{$testConfig{'TestCodeOptions'}});

    # Append local source files to be compiled to global configuration parameter
    push(@gaTestSrcFiles, @{$testConfig{'TestSourceFiles'}});

        # Append local options to global configuration parameter
    push(@gaProductCodeOptions, @{$testConfig{'ProductCodeOptions'}});

    # Append local source files to be compiled to global configuration parameter
    push(@gaProductSrcFiles, @{$testConfig{'ProductSourceFiles'}});

    # Append local include paths to global configuration parameter
    push(@gaIncludePaths, @{$testConfig{'IncludePaths'}});

    push(@gaLinkerOptions, @{$testConfig{'LinkerOption'}});
}

# This function checks the validity of input run type.
# If it is not valid, stops this program with error message.
sub CheckInputRunType
{
    # Is input run type valid?
    if(
        ($RunType eq 'Make')  or
        ($RunType eq 'Build') or
        ($RunType eq 'Clear')
      )
    {
        # Input RunType is OK! Do nothing.
    }
    else
    {
        # No, exit with message
        printf("Please input Make or Build or Clear as a second parameter.\n");
        printf("If the second parameter is nothing, it will execute Make.\n");
        exit(1);
    }
}

# This function executes make process according to the input run type.
# And return the compile state and clear state.
sub ExecMakeFileProcess
{
    # Result of 'Make' or 'Build'
    my $isExeValid = FALSE;

    # The object files has been cleared?
    my $IsCleared;

    # Check the input run type
    if ($RunType eq 'Make')
    {
        # The run type is 'Make'
        # Call Make function and save the status
        $isExeValid = (Makefile_Make() == EXECUTABLE_VALID);

        # The object is NOT cleared.
        $IsCleared = FALSE;
    }
    elsif ($RunType eq 'Build')
    {
        # The run type is 'Build'
        # Call Build function and save the status
        $isExeValid = (Makefile_Build() == EXECUTABLE_VALID);

        # The object is NOT cleared.
        $IsCleared = FALSE;
    }
    elsif ($RunType eq 'Clear')
    {
        # The run type is 'Clear'
        # Call Clear function
        Makefile_Clear();

        # The object is cleared.
        $IsCleared = TRUE;
    }

    # Returns the status
    return ($isExeValid, $IsCleared);
}

# This function executes the generate executable file
# according to the result of compilation.
sub ExecuteTestWithMessage
{
    # $IsNoCompileError: Compilation result
    # $IsCleared: Has object files cleared or not
    my ($isExeValid, $IsCleared) = @_;

    # The object files cleared?
    if ($IsCleared)
    {
        # Then, it can't execute it. Just output message.
        printf("\n***** Clear Done  *****\n\n");
    }
    else
    {
        # object files has been not cleared.
        # Check the compilation finished without or with error.
        if($isExeValid)
        {
            # The valid executable file is exists, then execute it!
            printf("\n***** Now execute the test code! *****\n\n");
            system($gTargetPath);
        }
        else
        {
            # The Compilation finished with error. Just output message.
            printf("\n***** Some Errors detected...  *****\n\n");
        }
    }
}

# main code
sub main
{
    InitializeGlobalVariablesFromCommandLineArguments();

    RemoveObjIfTheConfigFilesUpToDate();

    CheckInputRunType();

    CheckExistenceOfTheTestModule();

    SaveHarnessConfiguration();

    SaveTestConfiguration();

    # Make/Build/Clean Harness Codes
    Makefile_Init($gTargetPath, $gCompiler, \@gaIncludePaths, \@gaLinkerOptions);

    Makefile_AddSrc(\@gaHarnessSrcFiles, \@gaHarnessOptions, $gHarnessObjPath);

    Makefile_AddSrc(\@gaTestSrcFiles, \@gaTestCodeOptions, $gTestObjPath);

    Makefile_AddSrc(\@gaProductSrcFiles, \@gaProductCodeOptions, $gTestObjPath);

    my ($isExeValid, $IsCleared) = ExecMakeFileProcess();

    ExecuteTestWithMessage($isExeValid, $IsCleared);

    return 0;
}

main();

