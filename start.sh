#!/bin/bash


STRING="P2P Starting..."
echo $STRING

if [ -z ${1+x} ]; then
    echo "Need to specify number of peers"
    exit 1
else echo "Starting $(($1 + 1)) peers"
     # Start first peer
     echo "python3 iot.py 5000 &"
     python3 iot.py 5000 &
     sleep 5

     #Start the rest and join first peer
     COUNT=$1
     while [ $COUNT -gt 0 ]; do
	 echo "python3 iot.py $((5000 + COUNT)) 5000 &"
	 python3 iot.py $((5000 + COUNT)) 5000 &
	 let COUNT=COUNT-1
     done
fi
