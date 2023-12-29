#!/bin/bash

########################################
echo 'Copy files...'
cp -rfv app/ /root/app
cp -rfv scripts/* /root/app/
cp -rfv systemd/sensors.service /etc/systemd/system/sensors.service
#########################################
echo 'Setup the web service...'
systemctl daemon-reload
systemctl enable sensors.service
#########################################
echo 'Prepare the required modules...'
python3 -m pip install --upgrade pip
pip3 install --upgrade -r requirements.txt
#########################################
echo 'Start the service...'
systemctl start sensors.service
