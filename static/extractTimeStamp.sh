#! /bin/bash

# Timestamp is in milliseconds

json=$1

if [ $# -eq 0 ]; then
  echo "Specify json file"
  exit 1
fi

timeStamp=`head -n 30 $json | sed -n '29p' | cut -c18-`
date -d @$(echo "$timeStamp / 1000" | bc) +"%Y-%m-%d %H:%M:%S" 
