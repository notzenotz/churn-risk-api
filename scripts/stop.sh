#!/bin/bash
# Stop the old version before the new files are copied in.
systemctl stop churn-api 2>/dev/null || true
