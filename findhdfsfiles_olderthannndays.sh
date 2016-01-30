#!/bin/bash
#A script to find hdfs files older than N days in a directory.
#Normal hdfs list command has high latency and creates a load
#This script gets the HDFS image file and work on it.
usage="Usage: dir_diff.sh [days]"

if [ ! "$1" ]
then
  echo $usage
  exit 1
fi

#set the following variable to the namenode hostname
HOST="" 

now=$(date +%s)
curl "http://$HOST:50070/getimage?getimage=1&txid=latest" > img.dump
hdfs oiv -i img.dump -o fsimage.txt
cat fsimage.txt | grep "^d" | while read f; do 
  dir_date=`echo $f | awk '{print $6}'`
  difference=$(( ( $now - $(date -d "$dir_date" +%s) ) / (24 * 60 * 60 ) ))
  if [ $difference -gt $1 ]; then
    echo $f;
  fi
done
