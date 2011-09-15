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
# TODO
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

