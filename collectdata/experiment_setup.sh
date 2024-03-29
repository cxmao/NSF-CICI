#!/bin/bash
#Run experimental set-up and clean-up

# Experiment 2 Large Periodic
# Clean-up downloaded files 
echo "rm -r -f /home/ross/globus_files/*" | sudo at 11:55 PM 04/24/2019
# Collect Journal logs 
sudo journalctl -u globus.service --since "2019-04-24" > ../data/experiment1/journal2019-04-24.txt |sudo at 11:50 PM 04/24/2019
# Set-up Globus workload
sudo systemctl stop globus.service | sudo at 11:59 PM 04/24/2019
sudo systemctl start globus_large.service | sudo at 12:00 AM 04/25/2019

# Experiment 3 Small Periodic
echo "rm -r -f /home/ross/globus_files/*" | sudo at 11:55 PM 04/25/2019 
sudo journalctl -u globus.service --since "2019-04-25" > ../data/experiment2/journal2019-04-25.txt |sudo at 11:50 PM 04/25/2019 
sudo systemctl stop globus_large.service | sudo at 11:59 PM 04/25/2019
sudo systemctl start globus_small.service | sudo at 12:00AM 04/26/2019

# Experiment 4 Random Random
echo "rm -r -f /home/ross/globus_files/*" | sudo at 11:55 PM 04/26/2019
sudo journalctl -u globus.service --since "2019-04-26" > ../data/experiment3/journal2019-04-26.txt | sudo at 11:50 PM 04/26/2019
sudo systemctl stop globus_small.service | sudo at 11:59 PM 04/26/2019
sudo systemctl start globus.service | sudo at 12:00AM 04/27/2019

# Experiment 5 Large Random
echo "rm -r -f /home/ross/globus_files/*" | sudo at 11:55 PM 04/27/2019
sudo journalctl -u globus.service --since "2019-04-27" > ../data/experiment4/journal2019-04-27.txt | sudo at 11:50 PM 04/27/2019 
sudo systemctl stop globus.service | sudo at 11:59 PM 04/27/2019
sudo systemctl start globus_large.service | sudo at 12:00AM 04/28/2019

# Experiment 6 Small Random
echo "rm -r -f /home/ross/globus_files/*" | sudo at 11:55 PM 04/28/2019
sudo journalctl -u globus.service --since "2019-04-28" > ../data/experiment5/journal2019-04-28.txt | sudo at 11:50 PM 04/28/2019 
sudo systemctl stop globus.service | sudo at 11:59 PM 04/28/2019
sudo systemctl start globus_small.service | sudo at 12:00AM 04/29/2019


sudo journalctl -u globus.service --since "2019-04-29" > ../data/experiment5/journal2019-04-29.txt | sudo at 11:50 PM 04/29/2019 

~                                                                                                     
~                                                                                                     
~                                                                                                     
~                                                                                                     
~                                                                                                     
~                                                                                                     
~                                                                                                     
~                                         
