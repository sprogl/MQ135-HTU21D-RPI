#!/bin/bash

cp -rfv app/ /root/app
cp -rfv scripts/* /root/app/
cp -rfv systemd/sensors.service /etc/systemd/system/sensors.service

systemctl daemon-reload
systemctl enable sensors.service

python3 -m pip install --upgrade pip
pip3 install --upgrade -r requirements.txt

systemctl start sensors.service
