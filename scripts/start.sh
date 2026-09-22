#!/bin/bash
# Start the new version.
set -euo pipefail
systemctl enable churn-api
systemctl restart churn-api
