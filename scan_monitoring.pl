#!/usr/bin/perl
use LWP::UserAgent;
use Term::ANSIColor qw(:constants);
$Term::ANSIColor::AUTORESET = 1;
#--------------------------------------------------------------------------------
#scan_monitoring v1.0
#This script will scan a monitoring page and take necessary actions based on the error
#--------------------------------------------------------------------------------
#This first array will scan the monitoring page and create array with one entry for each alert.
#the scanning part is a bash script running curl, see it in the same repo
my @first_array = qx{getalerts.sh};
chomp @first_array;

#This is the main of the script, it will create a key/value pair of each parameter of every alerting host
#and calls the approprate procedure to handle the error
foreach $entry(@first_array){
	my @temp_array = split(',',$entry);
	my %hash_val = ();
	foreach $param (@temp_array){
		my($key,$val) = split(':',$param);
		$hash_val{$key} = $val;
	}
	if(($hash_val{'function'} =~ /xxxxxx|xxxxxx/) && (($hash_val{'error'} eq 'ConnectionRefused') || ($hash_val{'error'} eq 'TimedOut') {
		handle_error_1($hash_val{'hostname'},$hash_val{'function'});
	}
	elsif(($hash_val{'function'} =~ /xxxxxxxxx/) && ($hash_val{'error'} eq 'Noanswerfromhost')){
		handle_error_2($hash_val{'hostname'});
	}
	}
	else{
	}
}

#A sub to handle "Connection refused" or "timed out", it basically restarts service by sending a post request 
sub handle_error_1{
	my $pid = fork;
	return if $pid;
	my ($host,$fName) = @_;
	chomp $host;
	print RED "$host ";
	print RESET;
	print "with function $fName is connection refused or timed out, NUKE in progress...\n";
	my $ua = new LWP::UserAgent;
	$ua->post('$URL',
	[
	function => "$fName",
	description => 'xxxxxxxx',
	hostname => "$host",
	userid => '$user',
	site => 'xxxx',
	action => 'xxxxxx',
	]);
	print GREEN "Restarted service on $host \n";
	exit;
}

#A sub to handle "No answer from host",runs the pcycle bash script 
sub handle_error_2{
	my $host = shift;
	chomp $host;
	print RED "$host";
	print RESET;
	print " is down, power cycle in progress...\n";
	print "	pcycle.sh $host\n";
}
