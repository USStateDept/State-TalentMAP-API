#!/bin/bash
# wait-for-oracle.sh

set -e

host="$1"
user="$2"
password="$3"
suffix="$4"
shift

createUser() {
  echo exit | /opt/oracle/instantclient_19_8/sqlplus -L "$user"/"$password"@//"$host" "$suffix" @create-oracle-user.sql | grep -q 'Grant succeeded'
}

retries=300
while ((retries > 0)); do
    if createUser; then
        >&2 echo "User created!"
        exit 0
    else
    >&2 echo "Waiting for Oracle to accept writes..."
    sleep 10
    ((retries --))
    fi
done
    >&2 echo "Failed to write user to Oracle - max retries reached. Exiting..."
    exit 1
