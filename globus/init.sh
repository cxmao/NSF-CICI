#!/usr/bin/env bash 
#
#


#GLOBAL 
DTN="//newy-dtn.es.net:2811/data1/100G.dat" 
DEST="/home/cmao/share/"
FLOWS="4"


#INITIALIZE 

 globus-url-copy -vb -fast -p 4 ftp:$DTN file:$DEST
