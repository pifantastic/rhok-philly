#!/usr/bin/perl -w

use strict;
my $splitsize = 107; 	# Arbitrary number, how many entries to have per
			# target CSV
main();

##############################################
# tempslicer.pl
#
# A script to take pre-prepared comprehensive temperature data (CSV)
#	files and chop them into less-comprehensive temperature
#	data files, so the updater script can be tested.
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
		grep {-f $_} # From all files
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
my $fn_iter = 1;
my $line_iter = 0;
open(SRC, $srcfile) || die "Failed to open [$srcfile]:$!\n";
my $headerline = readline(SRC);
my $targfile = correct_targ_filename("$targdir/$fn", $fn_iter);
open(TARG, ">$targfile") || die "Failed to open [$targfile]:$!\n";
print TARG $headerline;

while(my $datline = <SRC>)
	{
	if($line_iter > $splitsize)
		{ # Reopen to new FN
		close(TARG);
		$fn_iter++;
		$targfile = correct_targ_filename($targdir/$fn, $fn_iter);
		open(TARG, ">$targfile") || die "Failed to open [$targfile]:$!\n";
		print TARG $headerline;
		$line_iter = 0;
		}
	print TARG $datline;
	$line_iter++;
	}
close(TARG);
close(SRC);
}

sub correct_targ_filename
{ # Add _suffix into filename before extension
my($tfn, $offset) = @_;
$tfn =~ s/\./_$offset\./;
return $tfn;
}


sub handle_args
{
my @args = @_;

if(@args != 2)
	{
	die "Usage: tempslicer.pl SRCDIR TARGDIR\n";
	}
if(! -d $args[0])
	{
	die "Usage: tempslicer.pl SRCDIR TARGDIR\nSRCDIR does not exist\n";
	}
if(-d $args[1])
	{
	die "Usage: tempslicer.pl SRCDIR TARGDIR\nTARGDIR must not exist\n";
	}
mkdir($args[1]) || die "Failed to make TARGDIR [$args[1]]:$!\n";
return ($args[0], $args[1]);
}

