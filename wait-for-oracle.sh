#!/bin/bash
# wait-for-oracle.sh

set -e

host="$1"
shift

checkOracle() {
  echo exit | /opt/oracle/instantclient_19_6/sqlplus -L talentmap/newpassword@//"$host"/ORCLPDB1.localdomain @healthcheck.sql | grep -q 'ID'
}

retries=30
while ((retries > 0)); do
    if checkOracle; then
        >&2 echo "Connected to Oracle!"
        exit 0
    else
    >&2 echo "Waiting for Oracle to accept connections..."
    sleep 10
    ((retries --))
    fi
done
    >&2 echo "Failed to connect to Oracle - max retries reached. Exiting..."
    exit 1
