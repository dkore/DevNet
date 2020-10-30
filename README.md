# BMS_Configuration
To bind the multiple switches with VLan for bms automation

| :exclamation:  External repository notice   |
|:---------------------------|
| This repository is now mirrored at "PLEASE UPDATE HERE - add External repo URL after code review is completed"  Please inform a https://github.com/gve-sw/ organization admin of any changes to mirror them to the external repo |
## Contacts
* Raveesh V
* Darshan Kore
* Vikram Goda
* Nupur Jain

## Solution Components
*  Python
*  Paramiko
*  CSV

## Python Setup
```shell script
# create virtual environment
python3 -m venv venv

#activate virtual environment
source venv/bin/activate

#install dependent modules
pip install -r Requirements.txt
```

## Configuration
>Modify **switches.csv** and **network.csv** with required details

```python
switches.csv
switch,hostname,port,username,password
s1,<hostname/IP>,22,<username>,<password>

network.csv
switch,vlanid,ipaddress,mac,interface
s1,x,<x.x.x.x>,xxxx.xxxx.xxx,xxx/x/1

```

## Usage

>Execute the following command to start the script

    $ python apply_configuration.py -c network.csv -s switches.csv

# Screenshots

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
