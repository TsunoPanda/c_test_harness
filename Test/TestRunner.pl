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

# Global compiler options
my @gaOptions = ();

# Global source files to be compiled
my @gaSourceFiles = ();

# Global include paths
my @gaIncludePaths = ();

use constant TEST_CODE_PATH => 'TestCode';
use constant LOCAL_CONFIG_FILE => 'MakeConfig.pl';
use constant GLOBAL_CONFIG_FILE => 'MakeConfig.pl';

### End of Global Configuration Parameters ###

# Test module name from the first command line argument
our $TestModule;

# Test run type from the second command line argument
our $RunType;

# Folder which has test codes, make configuration file to be executed
our $testModuleFolder;

# Folder where compilation result to be stored
our $gObjPath;

# The executable file name to be generated
our $gTargetName;

# Generic used value. false and true
use constant FALSE => (1==0);
use constant TRUE  => (0==0);

sub GetGlobalConfigPath
{
    # Make the global make configuration file path
    my $globalConfigPath = './'.GLOBAL_CONFIG_FILE;

    # The configuration file exist?
    unless(-e $globalConfigPath)
    {
        # It did not exist.
        printf("Could not find the ".LOCAL_CONFIG_FILE." in the same folder with this script.\n");
        exit(1);
    }

    return($globalConfigPath);
}

sub GetTheLocalConfigPath
{
    # Make the local make configuration file path
    my $localConfigPath = './'.TEST_CODE_PATH.'/'.$TestModule.'/'.LOCAL_CONFIG_FILE;

    # The configuration file exist?
    unless(-e $localConfigPath)
    {
        # It did not exist.
        printf("Could not find the ".LOCAL_CONFIG_FILE." in the test module folder\n");
        exit(1);
    }

    # Save the local configuration parameter
    return($localConfigPath);
}

sub isTheConfigFilesUpToDate
{
    # Make the global make configuration file path
    my $globalConfigPath = GetGlobalConfigPath();
    my $localConfigPath = GetTheLocalConfigPath();

    my @objfiles = glob( $gObjPath . '/*' );

    if (TimeStampComp_IsTheFileLatest($globalConfigPath, \@objfiles) == TRUE)
    {
        return TRUE;
    }

    if (TimeStampComp_IsTheFileLatest($localConfigPath, \@objfiles) == TRUE)
    {
        return TRUE;
    }

     return FALSE;
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
    $gTargetName = $TestModule.'Test.exe';

    # Make folder path where the object files are saved
    $gObjPath = $testModuleFolder.'/Obj';

    if ($RunType eq 'Make')
    {
        if (isTheConfigFilesUpToDate() == TRUE)
        {
            printf("!!! The make configure files are updated. Do Build.!!!\n");
            $RunType = 'Build';
        }
    }
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
sub SaveGlobalConfiguration
{
    # Path to the global make configuration file
    my $globalConfigPath = GetGlobalConfigPath();

    # Fetch the local configuration
    my %GlobalConfig = do $globalConfigPath;

    # Save the compiler command
    $gCompiler = $GlobalConfig{'Compiler'};

    # Append local options to global configuration parameter
    push(@gaOptions, @{$GlobalConfig{'Options'}});

    # Append local source files to be compiled to global configuration parameter
    push(@gaSourceFiles, @{$GlobalConfig{'SourceFiles'}});

    # Append local include paths to global configuration parameter
    push(@gaIncludePaths, @{$GlobalConfig{'IncludePaths'}});
}

# This function reads local make configuration file, and 
# saves them into global variables
sub SaveLocalConfiguration
{
    # Path to the make configuration file of the test module
    my $localConfigPath = GetTheLocalConfigPath();

    # Fetch the local configuration
    my %LocalConfig = do $localConfigPath;

    # Append local options to global configuration parameter
    push(@gaOptions, @{$LocalConfig{'Options'}});

    # Append local source files to be compiled to global configuration parameter
    push(@gaSourceFiles, @{$LocalConfig{'SourceFiles'}});

    # Append local include paths to global configuration parameter
    push(@gaIncludePaths, @{$LocalConfig{'IncludePaths'}});
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
            system($gObjPath.'/'.$gTargetName);
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

    CheckInputRunType();

    CheckExistenceOfTheTestModule();

    SaveGlobalConfiguration();

    SaveLocalConfiguration();

    Makefile_Init($gTargetName, $gCompiler, \@gaOptions, \@gaSourceFiles, \@gaIncludePaths, $gObjPath);

    my ($isExeValid, $IsCleared) = ExecMakeFileProcess();

    ExecuteTestWithMessage($isExeValid, $IsCleared);

    return 0;
}

main();

