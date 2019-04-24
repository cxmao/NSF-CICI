# AUTHOR: Christina Mao
# DATE: 03-11-2018
# DESCRIPTION:Run Globus transfers randomly between a period of 1 minutes to 30 minutes
# Files are selected by small (up to 1G), medium (up to 50G), and large (up to 500G)
# Files are pulled randomly according to a distribution
# A new distribution is selected randomly each day
# Guide to run ESnet DTN: https://fasterdata.es.net/performance-testing/DTNs/
# Not working for star, newy dtns
# Sleeps randomly within a 1 hour interval
# Output file names and timestamps to log file
#=================================================================================================

LOG_FILE="globus_records.txt"

#GLOBUS PARAMETERS
DTNS=("//cern-dtn.es.net" "//sunn-dtn.es.net" "//star-dtn.es.net")
DATASETS=("/data1/500G.dat" "/data1/100G.dat" "/data1/50G.dat" "/data1/10G.dat" "/data1/1G.dat"  "/data1/100M.dat")
CLIMATEDATA=("/data1/Climate-Huge" "/data1/Climate-Large" "/data1/Climate-Medium" "/data1/Climate-Small")

#changing SMALLDATA to the only used list, just ignore the name
SMALLDATA=("//data1/10M.dat" "//data1/50M.dat" "//data1/100M.dat" "//data1/1G.dat" "//data1/10G.dat" "//data1/50G.dat")

MEDIUMDATA=("//data1/10G.dat" "//data1/50G.dat" "//data1/100G.dat")
LARGEDATA=("//data1/100G.dat" "//data1/500G.dat")

#Climate data on one day, otherwise use normal data files

#Time of day to clean the file transfer directory
DELETE_TIME=12
#Don't remove file more than once during that hour
REMOVED_SWITCH=false

# Destination directory for file transfers
# Make sure no important files are there, it gets deleted
DEST="/home/ross/globus_files/"
FLOWS=$(shuf -i 4-8 -n 1)
PROTOCOL="ftp"
#TIME BETWEEN TRANSFERS IN SECONDS
INTERVAL=1800

#echo "testing" > $LOG_FILE
while true; do
        #Start the iperf3 server
        iperf3 -s -D
        curr_time=$(date +"%H")
        rand_file=$(($RANDOM % 100 + 1))
        interval=$(($RANDOM % 1740 + 60))
        echo $interval "seconds until next transfer"
        sleep $interval
        date_var=$(date)
        echo -n $date_var >> $LOG_FILE

        if [[ $curr_time -eq $DELETE_TIME ]] && ! $REMOVED_SWITCH
        then
                echo "removing files" >> $LOG_FILE
                rm -r -f "$DEST"*
                REMOVED_SWITCH=true
                echo $REMOVED_SWITCH
        elif $REMOVED_SWITCH && [[ $curr_time -ne $DELETE_TIME ]]
        then
                echo "new day" >> $LOG_FILE
                REMOVED_SWITCH=false
        fi
        #sleep_time=$(($RANDOM % $INTERVAL + 1))
        #sleep $sleep_time
        i=$(( $RANDOM % ${#DTNS[@]}))
        y=$(( $RANDOM % ${#DATASETS[@]}))
        s=$(( $RANDOM % ${#SMALLDATA[@]}))
        m=$(( $RANDOM % ${#MEDIUMDATA[@]}))
        l=$(( $RANDOM % ${#LARGEDATA[@]}))
        echo -n " " >> $LOG_FILE
        echo -n ${DTNS[i]} >> $LOG_FILE
        echo -n " " >> $LOG_FILE

        # Start Globus transfer
        # grab a small file from a random dtn
        echo ${SMALLDATA[s]} >> $LOG_FILE
        globus-url-copy -r -vb -fast -tcp-bs 64M -bs 1M -p $FLOWS -stripe ftp:${DTNS[i]}:2811${SMALLDATA[s]} file:$DEST

        globus_pid=$!
        echo $globus_pid
        wait $globus_pid
        #echo "Globus finished transfer" >> $LOG_FILE
done
