#!/usr/bin/env bash 
#
# AUTHOR: Christina Mao 
# DATE: 01-29-2018
# DESCRIPTION:
#=================================================================================================================
#
#GLOBAL 
#
#=================================================================================================================
#GLOBUS PARAMETERS
DTN="//newy-dtn.es.net:2811/data1/100G.dat" 
DEST="/home/cmao/share/"
FLOWS="4"

#=================================================================================================================
# BRO PARAMETERS
BRODIR="./Brologs"
NETWORK_INTERFACE="eth3"
BROSCRIPT="local.bro" 
#=================================================================================================================

#=================================================================================================================
#
# INITIALIZE
#
#=================================================================================================================
# TODO: Start Bro and Redirect LOGS
# Check if directory exists, if not then create it 
if [[ -d $BRODIR ]]; then 
	echo $BRODIR "exists"
elif [[ ! -d $BRODIR ]]; then
	echo "Creating directory: " $BRODIR 
	#TODO: INPUT SANITIZATION
	mkdir $BRODIR
fi
# Change directory and call Bro 
cd $BRODIR
echo pwd
/usr/local/zeek/bin/bro -i $NETWORK_INTERFACE $BROSCRIPT

# Start Globus transfer
 #globus-url-copy -vb -fast -p $FLOWS ftp:$DTN file:$DEST


# COLLECT DATA
#To-do: COLLECT PROC DATA

