use strict;

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


my $FILE1_IS_NEW   = 0;
my $FILE2_IS_NEW   = 1;
my $SAME_TIMESTAMP = 2;
sub CompareFileTimestamp
{
    my ($file1, $file2) = @_;

    my %MonthNameToIdx = 
    (
        "Jan" => 1,
        "Feb" => 2,
        "Mar" => 3,
        "Apr" => 4,
        "May" => 5,
        "Jun" => 6,
        "Jul" => 7,
        "Aug" => 8,
        "Sep" => 9,
        "Oct" => 10,
        "Nov" => 11,
        "Dec" => 12,
    );

    my @filestat1 = stat $file1;
    my @filestat2 = stat $file2;

    my $mtime1 = localtime($filestat1[9]); # 更新時刻
    my $mtime2 = localtime($filestat2[9]); # 更新時刻

    my $month1;
    my $dayNum1;
    my $hour1;
    my $minute1;
    my $second1;
    my $year1;
    if ($mtime1 =~ /([A-Za-z]+) ([A-Za-z]+) (\d+) (\d+)\:(\d+)\:(\d+) (\d+)/)
    {
        $month1  = %MonthNameToIdx{$2};
        $dayNum1 = $3;
        $hour1   = $4;
        $minute1 = $5;
        $second1 = $6;
        $year1   = $7;
    }

    my $month2;
    my $dayNum2;
    my $hour2;
    my $minute2;
    my $second2;
    my $year2;
    if ($mtime2 =~ /([A-Za-z]+) ([A-Za-z]+) (\d+) (\d+)\:(\d+)\:(\d+) (\d+)/)
    {
        $month2  = %MonthNameToIdx{$2};
        $dayNum2 = $3;
        $hour2   = $4;
        $minute2 = $5;
        $second2 = $6;
        $year2   = $7;
    }

    if ($year2 < $year1)
    {
        return $FILE1_IS_NEW;
    }
    elsif($year1 < $year2)
    {
        return $FILE2_IS_NEW;
    }

    # the year was same, lets compare the month
    if ($month2 < $month1)
    {
        return $FILE1_IS_NEW;
    }
    elsif ($month1 < $month2)
    {
        return $FILE2_IS_NEW;
    }

    # the month was same, lets compare the day
    if ($dayNum2 < $dayNum1)
    {
        return $FILE1_IS_NEW;
    }
    elsif ($dayNum1 < $dayNum2)
    {
        return $FILE2_IS_NEW;
    }

    # the day was same, lets compare the hour
    if ($hour2 < $hour1)
    {
        return $FILE1_IS_NEW;
    }
    elsif ($hour1 < $hour2)
    {
        return $FILE2_IS_NEW;
    }

    # the hour was same, lets compare the minute
    if ($minute2 < $minute1)
    {
        return $FILE1_IS_NEW;
    }
    elsif ($minute1 < $minute2)
    {
        return $FILE2_IS_NEW;
    }

    # the minute was same, lets compare the second
    if ($second2 < $second1)
    {
        return $FILE1_IS_NEW;
    }
    elsif ($second1 < $second2)
    {
        return $FILE2_IS_NEW;
    }

    return $SAME_TIMESTAMP;
}

sub CompileSources
{
    my ($optionStr, $includeStr) = @_;

    # Start compiling
    foreach my $src_obj (@src_objFilePath)
    {
        if (-e $src_obj->{obj}) #$src_obj->{obj} exist?
        {
            # TODO: Make .c->.h dependency here.

            if(CompareFileTimestamp($src_obj->{src}, $src_obj->{obj}) == $FILE1_IS_NEW)
            {
                # Source file is new. Let's compile.s
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

make()
