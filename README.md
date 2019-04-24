# NSF-CICI

## Useful References: 
[ESNET DTNs](https://fasterdata.es.net/performance-testing/DTNs/) 

[ESNET Switch Monitoring](https://graphite.es.net/west/)

## Experiment Setup Commands: 
### Setting up a Systemd Service: 
```
# Create a systemd unit file
sudo cp <unit file> /lib/systemd/system/
sudo chmod 644 <unit file> 
sudo systemctl daemon-reload #Reread the modified unit file 
sudo systemctl enable <unit file> #Starts service at boot
(reboot) 
sudo systemctl start <unit file> 
sudo systemctl restart <unit file> #Restart service
```
### To Check if background logging and Globus transfers are running: 
```
sudo systemctl status  collectstat.service  collectnet.service  collectinterrupt.service globus.service 
```
### Setting up Journalctl logging: 
Edit /etc/systemd/journal.conf: 
```
storage = persistent
```
Make a new directory to persistently store Journald logs, otherwise logs are stored in /run/log/journal which volatile on reboots. 
```
mkdir /var/log/journal
```
To check Journald logs: 
```
sudo journalctl --list-boots #shows previous boots
sudo journalctl -u globus.service -b <boot#>
```
### Hping Attacks: 
```
echo "<script location>" | sudo at <time> tomorrow
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
