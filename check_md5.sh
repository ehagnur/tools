#!/bin/bash
for status in $(md5sum -c md5sums.md5 |awk '{print $NF}') 
	do 
		if [[ $status == "OK" ]]; then 
			echo "Certificate is the same" 
		else 
			echo "Certificate has changed" 
		fi 
	done
