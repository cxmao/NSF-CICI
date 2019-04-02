#!/usr/bin/env bash
#
# AUTHOR: Christina Mao
# DATE: 04-02-2018
# DESCRIPTION:Run Globus transfers randomly according to a distribution
# Each interval, a small, medium, or large file is transferred 
# Guide to run ESnet DTN: https://fasterdata.es.net/performance-testing/DTNs/
# To-do: Not working for star, sunn dtns
# To-do: Sleep randomly in a 1 hour interval
#=================================================================================================

#GLOBUS PARAMETERS
DTNS=("//cern-dtn.es.net" "//newy-dtn.es.net" "//star-dtn.es.net" "//sunn-dtn.es.net")
DATASETS=("/data1/500G.dat" "/data1/100G.dat" "/data1/50G.dat" "/data1/10G.dat" "/data1/1G.dat"  "/data1/100M.dat")
CLIMATEDATA=("/data1/Climate-Huge" "/data1/Climate-Large" "/data1/Climate-Medium" "/data1/Climate-Small")
SMALLDATA=("//data1/100M.dat" "//data1/1G.dat" "//data1/Climate-Small")
MEDIUMDATA=("//data1/Climate-Medium" "//data1/10G.dat")
LARGEDATA=("//data1/Climate-Large" "//data1/100G.dat" "//data1/500G.dat")

#PERCENTAGE RANGE TO SELECT FILE 1-100
#if medium percentage is 60, and small is 30, 30-60 will trigger medium transfer
SMALL_PERCENT=50
MEDIUM_PERCENT=80
LARGE_PERCENT=100

DEST="/home/ross/globus_files/"
FLOWS=$(shuf -i 4-8 -n 1)
PROTOCOL="ftp"
#TIME BETWEEN TRANSFERS IN SECONDS
INTERVAL=3600

#while true; do

        rand_file=$(($RANDOM % 100 + 1))
        echo $rand_file
        sleep_time=$(($RANDOM % $INTERVAL + 1))
        sleep 1 #sleep $sleep_time
        i=$(( $RANDOM % ${#DTNS[@]}))
        y=$(( $RANDOM % ${#DATASETS[@]}))
        s=$(( $RANDOM % ${#SMALLDATA[@]}))
        m=$(( $RANDOM % ${#MEDIUMDATA[@]}))
        l=$(( $RANDOM % ${#LARGEDATA[@]}))
        echo ${DTNS[i]}

        # Start Globus transfer
        # random chance of grabbing a small file, medium file, or large file from a random dtn
        if [ $rand_file -lt $SMALL_PERCENT ]
        then
                echo "small"
                globus-url-copy -vb -fast -tcp-bs 64M -bs 1M -p $FLOWS -stripe ftp:${DTNS[i]}:2811${SMALLDATA[s]} file:$DEST
        elif [[ $rand_file -ge $SMALL_PERCENT ]] && [[ $rand_file -lt $MEDIUM_PERCENT ]]
        then
                echo "medium"
                globus-url-copy -vb -fast -tcp-bs 64M -bs 1M -p $FLOWS -stripe ftp:${DTNS[i]}:2811${MEDIUMDATA[m]} file:$DEST
        elif [ $rand_file -ge $MEDIUM_PERCENT ] && [[ $rand_file -lt $LARGE_PERCENT ]]
        then
                echo "large"
                globus-url-copy -vb -fast -tcp-bs 64M -bs 1M -p $FLOWS -stripe ftp:${DTNS[i]}:2811${LARGEDATA[l]} file:$DEST
        fi

                #globus-url-copy -vb -fast -tcp-bs 64M -bs 1M -p $FLOWS -stripe ftp:${DTNS[i]}:2811${DATASETS[y]} file:$DEST
        globus_pid=$!
        echo $globus_pid
        wait $globus_pid
        echo "Globus finished transfer"
#done
