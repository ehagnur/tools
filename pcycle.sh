#!/bin/bash
#This is a script to power cycle a host from the console using IPMI
#Either the physical hostname, or a VM hosted on the physical box can be passed a first argument
#There is a service to find the physical host for a given VM
usage(){
       echo
       echo "Usage: $0  hostname"
       echo "where:"
       echo "      hostname is the host you want to power cycle"
       echo
 }
URL="http://<hostname>/<service>"
if [ $# -ne 1 ]
then
    usage
    exit 1
fi
echo $1
LHOST=`echo $1|awk -F. '{print $1}'`
echo $LHOST                                                                                                    
PHOST_ORIG=`curl -s "http://$URL"|sed -n 6p |sed -e 's/"//g' -e 's/,//'|sed 's/ *//g'`
echo $PHOST_ORIG
PHOST_FQDN=`/usr/bin/host $PHOST_ORIG | awk '{print $1}'`
echo $PHOST_FQDN
       
if [[ $PHOST_FQDN =~ .*stratus.* ]]
then
   HLOM=`echo $PHOST_FQDN | sed 's/\.xxxxx/-sp\.stratus/'`
   echo "power cycling `/usr/bin/host $HLOM`"
   /usr/sbin/ipmitool -I lanplus -U console -f .racpasswd -H $HLOM power cycle
else
   HLOM=`echo $PHOST_ORIG | sed 's/^.*$/&-sp.con/'`
   echo "power cycling `/usr/bin/host $HLOM`"
   /usr/sbin/ipmitool -I lanplus -U console -f .racpasswd -H $HLOM power cycle
fi
