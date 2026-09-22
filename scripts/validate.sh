#!/bin/bash
# The deployment only counts as successful if the API answers /health within a minute.
for i in $(seq 1 30); do
  if curl -fs http://localhost/health > /dev/null; then
    echo "Churn Risk API is healthy"
    exit 0
  fi
  sleep 2
done
echo "Churn Risk API did not become healthy, last log lines:"
journalctl -u churn-api --no-pager -n 50
exit 1
