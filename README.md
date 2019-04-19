# NSF-CICI

## Useful References: 
[ESNET DTNs](https://fasterdata.es.net/performance-testing/DTNs/) \\
[ESNET Switch Monitoring](https://graphite.es.net/west/)

## Useful commands: 
### To Check if background logging and Globus transfers are running: 
```
sudo systemctl status  collectstat.service && systemctl status collectnet.service && systemctl status collectinterrupt.service  && systemctl status globus.service 
```

## Data on Kelewan:  
	* Collectl: /var/log/collectl/
	* Procfs: /home/cmao/Repos/nsf-cici/data/procfs/
	
## Workflow: 
1. Copy data files from Kelewan to local (/Repos/nsf-cici/data/<experiment_name>)
		* Collectl 
		* ProcFS/raw
2. Clean ProcFS raw files with clean_logs.py
	* Set File Date 
	* Set STATDIR 
	* Set NETDIR
	* Set OUTDIR </procfs/clean>
3. Run htm_procfs.py on each x_clean_csv file 
	* Set FILENAME
	* Set INPUT_DIR
	* Set OUT_DIR 
	* Check Model Parameters
4. Run plot_htm_scores.py 
	* Set DATE of the file 
