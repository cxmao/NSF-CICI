#!/usr/bin/env bash 
#
# AUTHOR: Christina Mao 
# DATE: 03-11-2018
# DESCRIPTION:Run Globus transfers randomly between a period of 5 minutes to 1 hour 
# Guide to run ESnet DTN: https://fasterdata.es.net/performance-testing/DTNs/	 
#=================================================================================================
# GLOBAL VARIABLES
DATESTAMP=$(date +"%Y-%m-%d")
TIMESTAMP=$(date +"%Y-%m-%d-%H:%M:%S")
echo $TIMESTAMP $DATESTAMP $PWD


#GLOBUS PARAMETERS
DTNS=("//cern-dtn.es.net" "//newy-dtn.es.net" "//star-dtn.est.net" "//sunn-dtn.es.net") 
DATASETS=("/data1/500G.dat" "/data1/100G.dat" "/data1/500M.dat" "/data1/100M")
CLIMATEDATA=("/data1/Climate-Huge" "/data1/Climate-Large" "/data1/Climate-Medium" "/data1/Climate-Small") 

DTN="//newy-dtn.es.net:2811/data1/10M.dat" 
DEST="/home/cmao/share/"
FLOWS="4"
PROTOCOL="ftp"

#while true; do

	sleep 1s
	i=$(( $RANDOM % ${#DTNS[@]}))
	y=$(( $RANDOM % ${#DATASETS[@]}))
	f=$(shuf -i 4-8 -n 1)
	echo $f	
	echo ${DTNS[i]}

	#for i in ${DTNS[@]}; do 
	#	echo $i
	#done

	# Start Globus transfer
	globus-url-copy -vb -fast -p $FLOWS ftp:${DTNS[i]}:2811${DATASETS[y]} file:$DEST 
	globus_pid=$!
	echo $globus_pid
	wait $globus_pid 
	echo "Globus finished transfer"
#done



