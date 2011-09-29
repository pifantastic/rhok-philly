#!/usr/bin/perl -w

use strict;
my $yearsearch = "/(1989|1990)";

main();

##############################################
# tempslicer2.pl
#
# A script to take pre-prepared comprehensive temperature data (CSV)
#	files and chop them into less-comprehensive temperature
#	data files, based on years, as a one-off script 
#
# This is the only bit of perl in this project, and it is
#	entirely standalone and not meant to do anything particularly
#	essential. It's just for testing.
##############################################

sub main
{
my @args = @ARGV;
my ($srcdir, $targdir) = handle_args(@args);
opendir(SRC, $srcdir);
my @to_parse = 	grep {$_ =~ /csv$/} # all csvs
		grep {-f "$srcdir/$_"} # From all files
		readdir(SRC); # In the sourcedir
closedir(SRC);
map
	{
	readsplit($_, $srcdir, $targdir);
	} @to_parse;
}

sub readsplit
{
my ($fn, $srcdir, $targdir) = @_;

my $srcfile = "$srcdir/$fn";
open(SRC, $srcfile) || die "Failed to open [$srcfile]:$!\n";
my $headerline = readline(SRC);
my $targfile = "$targdir/$fn";
open(TARG, ">$targfile") || die "Failed to open [$targfile]:$!\n";
print TARG $headerline;

while(my $datline = <SRC>)
	{
	next if($datline =~ /^,/); # Skip malformed lines. Sigh.
#	print "$srcfile D: $datline\n";
	next unless ($datline =~ /$yearsearch/); # Year restriction is the whole point
	print TARG $datline;
	}
close(TARG);
close(SRC);
}

sub handle_args
{
my @args = @_;

if(@args != 2)
	{
	die "Usage: tempslicer2.pl SRCDIR TARGDIR\n";
	}
if(! -d $args[0])
	{
	die "Usage: tempslicer2.pl SRCDIR TARGDIR\nSRCDIR does not exist\n";
	}
if(-d $args[1])
	{
	die "Usage: tempslicer2.pl SRCDIR TARGDIR\nTARGDIR must not exist\n";
	}
mkdir($args[1]) || die "Failed to make TARGDIR [$args[1]]:$!\n";
return ($args[0], $args[1]);
}

