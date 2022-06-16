# use our Spark cluster

## first setup

In `etc/hosts` add

```
# MAPD B COSMO
127.0.0.50	master.cosmo
127.0.0.51	slave1.cosmo
127.0.0.52      slave2.cosmo
```

In `.ssh/config` add
```
Host mapd_cloud_gate
    HostName gate.cloudveneto.it
    User fbarone
    LocalForward master.cosmo:2022 10.67.22.128:22
    LocalForward master.cosmo:1200 10.67.22.128:1200
    LocalForward master.cosmo:8080 10.67.22.128:8080
    LocalForward master.cosmo:4040 10.67.22.128:4040
    LocalForward master.cosmo:7077 10.67.22.128:7077
    LocalForward master.cosmo:8888 10.67.22.128:8888
    LocalForward master.cosmo:9092 10.67.22.128:9092
    LocalForward master.cosmo:5006 10.67.22.128:5006
    LocalForward slave1.cosmo:2022 10.67.22.252:22
    LocalForward slave2.cosmo:2022 10.67.22.240:22

Host master.cosmo
	HostName master.cosmo
	User root
	Port 2022

Host slave1.cosmo
	HostName slave1.cosmo
	User root
	Port 2022
	
Host slave2.cosmo
	HostName slave2.cosmo
	User root
	Port 2022
```
Remember to replace `YOURUSERNAME` with your cloud veneto username.


### port mapping

the master port are mapped this way:
- 1200 Jupyter Lab
- 8080 Spark Master UI
- 4040 Spark Application UI
- 7077 Spark Master SOCKET (do not use)
- 8888 boh, for whatever will use this port
- 9092 for Kafka broker
- 5006 for the COSMO dashboard


## logging into cluster

First, open a terminal on your local computer and run
```bash
ssh mapd_cloud_gate
```
Use your personal password for Cloud Veneto. This will open a tunnel on your local machine. Keep this terminal open in background.

Open another terminal, and ssh to the **master**:
```bash
ssh master.cosmo
```
Use the password of the virtual machine.


## start working!

Navigate to the project folder (I strongly suggest to do this!)
```bash
goto_project
```
```bash
spark_deploy
```

To run Jupyter Lab:
```bash
myjupyter
```
The Jupyter UI will be available in your browser to `master.cosmo:1200`. Keep the terminal open & work.


## stop working

1. Remember to stop Jupyter (close the terminal of the server)
2. Shut down the Spark cluster:
```bash
spark_stop
```