# yaticker

Stock and crypto ticker with different clients (console, cli and web)

## Prerequisites

If you run the client on the raspberry with the e-paper hat, you will need to install the required software prior to
this.
Follow the instructions on [their wiki](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT) under the tab "Hardware/Software setup"

## Install & Run

Copy the files from this repository, or clone using:
```
cd ~
git clone https://github.com/sebasrp/yaticker
cd yaticker
```

Install the required modules using pip
```
(optional but recommended) Use a virtual environment for this
pip install virtualenv (if you do not have it installed)
virtualenv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
pip install -e "git+https://github.com/waveshare/e-Paper.git#egg=waveshare_epd&subdirectory=RaspberryPi_JetsonNano/python"

```

Run the script using:
```
python3 src/yaticker/cli.py
```

## Configuration
The file `config.yaml` contains a number of options that you can tweak.
```
# whether to cycle through the watchlist or not.
# If set to False, will display first in list.
# If set to True, cycles throug watchlist
cycle: true
# Update frequency in seconds
updatefrequency: 5
# Displays volume
showvolume: false
watchlist:
    - AMZN
    - FB
    - APPL
# How many days to display
intervaldays: 1 
```
