#!/bin/bash
# Install the Python libraries and register the API as a system service.
set -euo pipefail
cd /opt/churn-api
if [ ! -x venv/bin/python ]; then
  python3.11 -m venv venv
fi
venv/bin/pip install --quiet --upgrade pip
venv/bin/pip install --quiet -r requirements.txt
cp deploy/churn-api.service /etc/systemd/system/churn-api.service
chown -R ec2-user:ec2-user /opt/churn-api
systemctl daemon-reload
