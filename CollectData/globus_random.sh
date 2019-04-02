#!/usr/bin/env bash 
#
# AUTHOR: Christina Mao 
# DATE: 03-11-2018
# DESCRIPTION:Run Globus transfers randomly between a period of 5 minutes to 1 hour 
# Guide to run ESnet DTN: https://fasterdata.es.net/performance-testing/DTNs/	 
# To-do: Not working for star, sunn dtns
# To-do: Sleep randomly in a 1 hour interval
#=================================================================================================

#GLOBUS PARAMETERS
DTNS=("//cern-dtn.es.net" "//newy-dtn.es.net" "//star-dtn.es.net" "//sunn-dtn.es.net") 
DATASETS=("/data1/500G.dat" "/data1/100G.dat" "/data1/50G.dat" "/data1/10G.dat" "/data1/1G.dat"  "/data1/100M.dat")
CLIMATEDATA=("/data1/Climate-Huge" "/data1/Climate-Large" "/data1/Climate-Medium" "/data1/Climate-Small") 

DEST="/home/cmao/share/"
FLOWS=$(shuf -i 4-8 -n 1)
PROTOCOL="ftp"

#while true; do

	sleep 1s
	i=$(( $RANDOM % ${#DTNS[@]}))
	y=$(( $RANDOM % ${#DATASETS[@]}))
	echo ${DTNS[i]}

	# Start Globus transfer
	globus-url-copy -vb -fast -p $FLOWS ftp:${DTNS[i]}:2811${DATASETS[y]} file:$DEST 
	globus_pid=$!
	echo $globus_pid
	wait $globus_pid 
	echo "Globus finished transfer"
#done



