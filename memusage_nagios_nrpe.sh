#!/bin/bash
# Setup standard Nagios/NRPE return codes
#
UNKNOWN_STATE=3
CRITICAL_STATE=2
WARNING_STATE=1
OK_STATE=0

#Define commands
FREE=/usr/bin/free
AWK=/bin/awk
EGREP=/bin/egrep
ECHO=/bin/echo

#Usage function
usage(){
cat <<EOF
Usage:
$0 -c <memory>
    where: memory - threshold value"
	
EOF
   exit ${UNKNOWN_STATE}
}

#Find the current physical memory usage
check_mem(){
	CURMEM=`$FREE |$EGREP 'buffers/cache'|$AWK '{print ($4/($3 + $4))*100}'|$AWK -F. '{print $1}'`

	#test if memory usage and exit
	if [[ $CURMEM -gt $CRITLEVEL ]]; then
	   $ECHO "CRITICAL - Physical memory usage ${CURMEM}% passed threshold"
	   exit ${CRITICAL_STATE}
	elif [[ $CURMEM -le $CRITLEVEL ]]; then
	   $ECHO "OK - Physical memory usage ${CURMEM}% under threshold"
	   exit ${OK_STATE}
	else
	   $ECHO "Unable to determine physical memory usage"
	   exit ${UNKNOWN_STATE}
	fi
}

#Check and Parse arguments
if [ $# -lt 2 ] || ! [[ $2 =~ ^[0-9]+$ ]]; then
   echo "Invalid input"
   usage
else
  while getopts ":c:" arg; do
    case $arg in
     c)
       CRITLEVEL=$OPTARG
       check_mem
       ;;
     \?)
       echo "Invalid option: -$OPTARG" >&2
       usage
       ;;
     esac
  done
fi
