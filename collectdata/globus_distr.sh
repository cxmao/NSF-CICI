#!/usr/bin/env bash
#
# AUTHOR: Christina Mao
# DATE: 04-02-2018
# DESCRIPTION:Run Globus transfers randomly according to a distribution
# Each interval, a small, medium, or large file is transferred 
# Guide to run ESnet DTN: https://fasterdata.es.net/performance-testing/DTNs/
# To-do: Not working for star, newy dtns
# To-do: Decide which files (only climate vs only GB.dat files vs mix)
# To-do: remove files after writing
#=================================================================================================

#GLOBUS PARAMETERS
DTNS=("//cern-dtn.es.net" "//sunn-dtn.es.net")
DATASETS=("/data1/500G.dat" "/data1/100G.dat" "/data1/50G.dat" "/data1/10G.dat" "/data1/1G.dat"  "/data1/100M.dat")
CLIMATEDATA=("/data1/Climate-Huge" "/data1/Climate-Large" "/data1/Climate-Medium" "/data1/Climate-Small")
SMALLDATA=("//data1/5GB-in-small-files/" "//data1/5MB-in-tiny-files" "//data1/100M.dat" "//data1/1G.dat")
MEDIUMDATA=("//data1/50GB-in-medium-files" "//data1/10G.dat")
LARGEDATA=("//data1/500GB-in-large-files" "//data1/Climate-Large/" "//data1/100G.dat" "//data1/500G.dat" "/data1/Climate-Large/" "/data1/Climate-Small/")

#Climate data on one day, otherwise use normal data files

#PERCENTAGE RANGE TO SELECT FILE 1-100
#if medium percentage is 60, and small is 30, 30-60 will trigger medium transfer
SMALL_PERCENT=50
MEDIUM_PERCENT=80
LARGE_PERCENT=100

#Time of day to clean the file transfer directory
DELETE_TIME=13
#Don't remove file more than once during that hour
REMOVED_SWITCH=false

# Destination directory for file transfers
# Make sure no important files are there, it gets deleted
DEST="/home/ross/globus_files/"
FLOWS=$(shuf -i 4-8 -n 1)
PROTOCOL="ftp"
#TIME BETWEEN TRANSFERS IN SECONDS
INTERVAL=3600

#while true; do
        curr_time=$(date +"%H")
        rand_file=$(($RANDOM % 100 + 1))
        echo $rand_file
        if [[ $curr_time -eq $DELETE_TIME ]] && [[ $REMOVED_SWITCH -eq false ]]
        then
                echo "removing files"
                rm -r -f "$DEST"*
                REMOVED_SWITCH=$((true))
        elif [[ $REMOVED_SWITCH -eq true ]] && [[ $curr_time -ne $DELETE_TIME ]]
        then
                echo "new day"
                REMOVED_SWITCH=$((false))
        fi
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
                globus-url-copy -r -vb -fast -tcp-bs 64M -bs 1M -p $FLOWS -stripe ftp:${DTNS[i]}:2811${SMALLDATA[s]} file:$DEST
        elif [[ $rand_file -ge $SMALL_PERCENT ]] && [[ $rand_file -lt $MEDIUM_PERCENT ]]
        then
                echo "medium"
                globus-url-copy -r -vb -fast -tcp-bs 64M -bs 1M -p $FLOWS -stripe ftp:${DTNS[i]}:2811${MEDIUMDATA[m]} file:$DEST
        elif [ $rand_file -ge $MEDIUM_PERCENT ] && [[ $rand_file -lt $LARGE_PERCENT ]]
        then
                echo "large"
                globus-url-copy -r -vb -fast -tcp-bs 64M -bs 1M -p $FLOWS -stripe ftp:${DTNS[i]}:2811${LARGEDATA[l]} file:$DEST
        fi

                #globus-url-copy -vb -fast -tcp-bs 64M -bs 1M -p $FLOWS -stripe ftp:${DTNS[i]}:2811${DATASETS[y]} file:$DEST
        globus_pid=$!
        echo $globus_pid
        wait $globus_pid
        echo "erasing files in " $DEST"*"
        #run this at the end of the day
        #rm -r -f "$DEST"*
        echo "Globus finished transfer"
#done
