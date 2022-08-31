use strict;
use lib qw(./);
use Makefile;
use Time::HiRes qw( usleep gettimeofday tv_interval );

############################################
##### Global Configuration Parameters ######
############################################
# The compiler command
my $gCompiler = 'gcc';

# Compiler options
my @gaOptions = (
    '-MMD',
);

# The source files to be compiled
my @gaSourceFiles = (
    './TestHarness/unity.c',
    './TestHarness/unity_fixture.c',
    './TestHarness/unity_memory.c',
);

# The include paths
my @gaIncludePaths = (
    './TestHarness/',
);

# The target executable file name
my $gTargetName = '';

# The folder path where the object files are saved
my $gObjPath = '';

sub SaveLocakConfiguration
{
    my ($localConfigPath) = @_;

    my %LocalConfig = do $localConfigPath;

    # Append local options
    push(@gaOptions, @{$LocalConfig{'Options'}});

    # Append local source files to be compiled
    push(@gaSourceFiles, @{$LocalConfig{'SourceFiles'}});

    # Append local include paths
    push(@gaIncludePaths, @{$LocalConfig{'IncludePaths'}});
}

############################################
###             Applications           #####
############################################

my $TestModule;
my $RunType;

if (@ARGV < 1)
{
    printf("Please input the test module as the first parameter.\n");
    exit(1);
}
elsif(@ARGV <2)
{
    $TestModule = $ARGV[0];
    $RunType    = 'Make';
}
else
{
    $TestModule = $ARGV[0];
    $RunType    = $ARGV[1];
}

unless(-d './TestCode/'.$TestModule)
{
    printf("Could not find the test module folder\n");
    exit(1);
}
my $localConfigPath = './TestCode/'.$TestModule.'/MakeConfig.pl';
SaveLocakConfiguration($localConfigPath);

$gTargetName = $TestModule.'Test.exe';

$gObjPath = './TestCode/'.$TestModule.'/Obj';

Makefile_Init($gTargetName, $gCompiler, \@gaOptions, \@gaSourceFiles, \@gaIncludePaths, $gObjPath);

if ($RunType eq 'Make')
{
    Makefile_Make();

    printf("\n***** Now execute the test code! *****\n\n");
    system($gObjPath.'/'.$gTargetName);
}
elsif ($RunType eq 'Build')
{
    Makefile_Build();

    printf("\n***** Now execute the test code! *****\n\n");
    system($gObjPath.'/'.$gTargetName);
}
elsif ($RunType eq 'Clear')
{
    Makefile_Clear();
}
else
{
    printf("Please input Make or Build or Clear as a second parameter.\n");
    printf("If the second parameter is nothing, it will execute Make.\n");
    exit(1);
}

