#!/bin/bash
# Setup standard Nagios/NRPE return codes
#
UNKNOWN_STATE=3
CRITICAL_STATE=2
WARNING_STATE=1
OK_STATE=0

#Define commands and variables
AWK=/bin/awk
SUDO=/usr/bin/sudo
HDFS=/usr/bin/hdfs
HADOOP=/usr/bin/hadoop
SED=/bin/sed
TAIL=/usr/bin/tail
GREP=/bin/grep
HOST=`/bin/hostname`

#get hadoop version
VERSION=`$HADOOP version|$TAIL -1|$SED 's/^.*cdh//'|$SED 's/.jar//'`
#get the safe mode value of a namenode
if [[ $VERSION =~ ^4.* ]]; then
    SAFEMODE=`$SUDO $HDFS dfsadmin -safemode get|$AWK '{print $NF}'`
elif [[ $VERSION =~ ^5.* ]]; then
    SAFEMODE=`$SUDO $HDFS dfsadmin -safemode get|$GREP $HOST|$AWK '{print $4}'` 
fi
#test Safemode status on namenode
case "$SAFEMODE" in
  "ON")
      echo "CRITICAL - Safemode is ON on $HOST"
      exit ${CRITICAL_STATE}
      ;;
  "OFF")
      echo "OK - Safemode is OFF on $HOST"  
      exit ${OK_STATE}
      ;;
  *)
      echo "Unable to check Safemode status on $HOST"
      exit ${UNKNOWN_STATE}
      ;;
esac
