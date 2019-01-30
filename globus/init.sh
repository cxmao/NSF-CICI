#!/usr/bin/env bash 
#
#


#GLOBAL 

DTN="//newy-dtn.es.net:2811/data1/100G.dat" 
DEST="/home/cmao/share/"
FLOWS="4"


# INITIALIZE
#To-do: Start Bro and Redirect LOGS

# Start Globus transfer
 globus-url-copy -vb -fast -p $FLOWS ftp:$DTN file:$DEST


# COLLECT DATA
#To-do: COLLECT PROC DATA

