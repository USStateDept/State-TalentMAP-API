#!/bin/bash
# wait-for-oracle.sh

set -e

host="$1"
user="$2"
password="$3"
suffix="$4"
alt="$5"
shift

checkOracle() {
  if $alt; then
    echo exit | /opt/oracle/instantclient_19_8/sqlplus -L "$user"/"$password"@//"$host" "$suffix" @healthcheck-alt.sql | grep -q 'USER'
  else
    echo exit | /opt/oracle/instantclient_19_8/sqlplus -L "$user"/"$password"@//"$host" "$suffix" @healthcheck.sql | grep -q 'READ WRITE'
  fi
}

retries=360
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
