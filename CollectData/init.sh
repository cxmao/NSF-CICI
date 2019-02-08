#!/usr/bin/env bash 
#
# AUTHOR: Christina Mao 
# DATE: 01-29-2018
# DESCRIPTION:
# To-Do:  
#	 
#================================================================================================================
#
# GLOBAL VARIABLES
#
#=================================================================================================================
PWD=$(pwd)
DATESTAMP=$(date +"%Y-%m-%d")
TIMESTAMP=$(date +"%Y-%m-%d-%H:%M:%S")
echo $TIMESTAMP $DATESTAMP $PWD


#GLOBUS PARAMETERS
DTN="//newy-dtn.es.net:2811/data1/10G.dat" 
DEST="/home/cmao/share/"
FLOWS="4"
PROTOCOL="ftp"

#BRO PARAMETERS
BRODIR=$PWD"/brologs"
BROLOGS="$TIMESTAMP"
BROPATH="$BRODIR"/"$BROLOGS""/"
NETWORK_INTERFACE="eth3"
BROSCRIPT="" 

#COLLECTL PARAMETERS
COLLECTLDIR=$PWD"/collectl" 
COLLECTLFILE="$TIMESTAMP" 
COLLECTLPATH="$COLLECTLDIR"/"$COLLECTLFILE"
COLLECTLCOMMAND="-sCD"
echo "Collectl data directory is:" $COLLECTLPATH
#=================================================================================================================
#
# INITIALIZE
#
#=================================================================================================================
# Create a directory to store Collectl data: 
if [[ -d $COLLECTLDIR ]]; then 
	echo $COLLECTLDIR "exists"
elif [[ ! -d $COLLECTLDIR ]]; then
	echo "Creating directory: " $COLLECTLDIR
	mkdir $COLLECTLDIR
	echo "Collectl data directory is:" $COLLECTLDIR
fi


# Create directory for bro logs and redirect to  BRODIR
if [[ -d $BROPATH ]]; then 
	echo $BROPATH "exists"
elif [[ ! -d $BROPATH ]]; then
	echo "Creating directory: " $BRODIR 
	mkdir $BRODIR
	cd $BRODIR
	mkdir $BROLOGS
	echo "Bro logs directory is:" $BROPATH
fi

# Change directory and initialize Collectl and Bro 
# Note: Bro creates logs in the directory it is called. If using Bro Cluster, the log directory can be specified. 
echo 'Changing directory to' $BROPATH
cd $BROPATH

# Start Collectl 
echo "Initializing  Collectl"
echo "Collectl output file is:" $COLLECTLPATH
collectl -sCD -P -f$COLLECTLPATH & 



# Start Bro
echo "Initializing Bro"
/usr/local/zeek/bin/bro -i $NETWORK_INTERFACE $BROSCRIPT &



# Start Globus transfer
#globus-url-copy -vb -fast -p $FLOWS ftp:$DTN file:$DEST
#globus_pid=$$
#echo $globus_pid
#================================================================================================================
# 
# TERMINATE 
#
#==============================================================================================================


#wait $globus_pid
#Terminate all children processes of Bro and Collectl 
for pid in $(ps -ef | grep "bro\|collectl" | awk '{print $3}');
	 do kill -9 $pid; 
done
echo "Done"

#================================================================================================================
# 
# PROCESS DATA 
#
#==============================================================================================================




