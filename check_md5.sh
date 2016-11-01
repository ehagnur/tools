#!/bin/bash
#1. Generate the md5 for the files that should be checked (md5sum <FILE>)
#2. Save the output to the md5sum.md5 file 
#example: md5sum.md file for two files (you can add as many files as you want)
#09f7e02f1290be211da707a266f153b3  sample_file
#f0ef7081e1539ac00ef5b761b4fb01b3  another_file
#take a backup of your file for later comparision(in this script 
#I am naming them the same with .orig extention)
#run this script to check for a change in file content
for check in $(md5sum -c md5sums.md5 2>/dev/null|sed 's/\s//g') 
do 
	fname=$(echo $check|awk -F':' '{print $1}')
	status=$(echo $check|awk -F':' '{print $2}')
		
	if [[ $status == "OK" ]]; then 
		echo "None of the file contents have been changed" 
	else 
		echo "Content has been changed for the following file"
 		backup=$(echo $fname|sed 's/^.*$/&.orig/')
 		/usr/sbin/sdiff $fname $backup
 	fi
done
