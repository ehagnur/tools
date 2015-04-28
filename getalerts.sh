#!/bin/bash
#This is a simple curl with multiple filtering to format HTML format file in to a recored for each alert on a monitoring page
URL="xxxxxx"
curl --insecure --silent $URL|sed -e '1,6 d' -e 's/\]//' -e '$ d' -e '/\},/d' -e '/\}/d' -e 's/\"//g' -e 's/\\n//g'|awk '/\{/{if (NR!=1)print "";next}{printf "%s ",$0}END{print "";}'|sed 's/ *//g'|sort -u -t, -k14
