package TimeStampComp;
use strict;
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(TimeStampComp_CompareFiles TimeStampComp_GetTimeStampValue);
our %TimeStampList = ();

our $FILE1_IS_NEW   = 0;
our $FILE2_IS_NEW   = 1;
our $SAME_TIMESTAMP = 2;

sub GetTimeStampValueByCheckingFileSystem
{
    my ($file) = @_;
    my @filestat = stat $file;
    my $file_time = $filestat[9]; # çXêVéûçè

    # save the file time
    $TimeStampList{$file} = $file_time;

    return $file_time;
}

sub TimeStampComp_GetTimeStampValue
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

    my $timestameValue1 = TimeStampComp_GetTimeStampValue($file1);
    my $timestameValue2 = TimeStampComp_GetTimeStampValue($file2);
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
