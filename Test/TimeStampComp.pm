package TimeStampComp;

use Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(TimeStampComp_CompareFiles);

our %TimeStampList = ();
our $FILE1_IS_NEW   = 0;
our $FILE2_IS_NEW   = 1;
our $SAME_TIMESTAMP = 2;

sub GetTimeStampValueByCheckingFileSystem
{
    my ($file) = @_;
    # | byte7 | byte6 | byte5 | byte4 | byte3 | byte2 | byte1 | byte0 |
    # |       |     year      | month |  day  | hour  |  min  |  sec  |

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

    my @filestat = stat $file;

    my $mtime = localtime($filestat[9]); # çXêVéûçè

    my $month;
    my $dayNum;
    my $hour;
    my $minute;
    my $second;
    my $year;
    if ($mtime =~ /([A-Za-z]+) ([A-Za-z]+) (\d+) (\d+)\:(\d+)\:(\d+) (\d+)/)
    {
        $month  = %MonthNameToIdx{$2};
        $dayNum = $3;
        $hour   = $4;
        $minute = $5;
        $second = $6;
        $year   = $7;
    }
    else
    {
        # TODO: Exception
    }

    my $timestameValue =   ($year   << 40)
                         + ($month  << 32)
                         + ($dayNum << 24)
                         + ($hour   << 16)
                         + ($minute << 8 )
                         + ($second << 0 );

    # save the value not to repeat this cacluration
    $TimeStampList{$file} = $timestameValue;

    return $timestameValue;

}

sub GetTimeStampValue
{
    my ($file) = @_;
    if (exists($TimeStampList{$file}))
    {
        # get the value from the hash.
        return $TimeStampList{$file};
    }
    else
    {
        return GetTimeStampValueByCheckingFileSystem($file);
    }
}

sub TimeStampComp_CompareFiles
{
    my ($file1, $file2) = @_;

    my $timestameValue1 = GetTimeStampValue($file1);
    my $timestameValue2 = GetTimeStampValue($file2);
    if ($timestameValue1 < $timestameValue2)
    {
        return $FILE2_IS_NEW;
    }
    elsif ($timestameValue1 > $timestameValue2)
    {
        return $FILE1_IS_NEW;
    }
    else
    {
        return $SAME_TIMESTAMP;
    }
}

1;
