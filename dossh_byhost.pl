#!/usr/bin/perl
#Script I use to ssh a list of hosts I put in a file whenever I want to take a batch action
#hosts.txt is a file containing a list of hosts
use Net::SSH::Perl;
use strict;
use Term::ReadKey;

print "Enter username: ";
my $user = <STDIN>;
chomp $user;
print "Enter password: ";
ReadMode 'noecho';
my $pass = ReadLine 0;
chomp $pass;
ReadMode 'normal';
print "\nEnter command: ";
my $cmd = <STDIN>;
chomp $cmd;
open(HOST,'hosts.txt');

while(<HOST>){
        chomp $_;
        my @ping_status = qx{ping -c 1 $_};
        print $_,"\n";
        if($ping_status[1] =~/^64/){
                #-- set up a new connection
                my $ssh = Net::SSH::Perl->new($_, protocol => '1,2');
                #-- authenticate
                $ssh->login($user, $pass);
                #-- execute the command
                my($stdout, $stderr, $exit) = $ssh->cmd($cmd);
                print $stdout,"\n";
        }
        else{
                print "is not reachable\n\n"
        }
}
close(HOST);
