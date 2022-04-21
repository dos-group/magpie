this folder is used to configure telegraf.
system service can be configured in `/usr/lib/systemd/system/telegraf.service`

1. change telegraf service
	located in `/usr/lib/systemd/system/telegraf.service`, change user to root and replace config file /etc/telegraf/telegraf.conf to your file 
	e.g., `sudo cp telegraf_osd.service /usr/lib/systemd/system/telegraf.service`

2. reload daemon service
	```bash
	systemctl daemon-reload
	```
3. restart telegraf service
	```bash
	service telegraf restart
	service telegraf status -l
	```

```bash
# CentOS lustre client
cd ~/app/telegraf
sudo cp telegraf_client.service /usr/lib/systemd/system/telegraf.service
sudo systemctl daemon-reload
sudo service telegraf restart
sudo service telegraf status -l

# Ubuntu lustre client
cd ~/app/telegraf
sudo cp telegraf_client.service /lib/systemd/system/telegraf.service
sudo systemctl daemon-reload
sudo service telegraf restart
sudo service telegraf status -l
```