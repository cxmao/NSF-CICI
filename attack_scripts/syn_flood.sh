# Setup the hping3 SYN flood experiment with iperf3
echo "/home/ross/testing/syn_12pm.sh" | sudo at 12pm tomorrow
echo "/home/ross/testing/syn_2pm.sh" | sudo at 2pm tomorrow
echo "/home/ross/testing/syn_4pm.sh" | sudo at 4pm tomorrow
echo "/home/ross/testing/syn_6pm.sh" | sudo at 6pm tomorrow
echo "iperf3 -c 10.40.1.1" | sudo at 1am tomorrow
echo "iperf3 -c 10.40.1.1" | sudo at 4am tomorrow
echo "iperf3 -c 10.40.1.1" | sudo at 7am tomorrow
echo "iperf3 -c 10.40.1.1" | sudo at 10am tomorrow
echo "iperf3 -c 10.40.1.1" | sudo at 1pm tomorrow
echo "iperf3 -c 10.40.1.1" | sudo at 4pm tomorrow
echo "iperf3 -c 10.40.1.1" | sudo at 7pm tomorrow
echo "iperf3 -c 10.40.1.1" | sudo at 10pm tomorrow
