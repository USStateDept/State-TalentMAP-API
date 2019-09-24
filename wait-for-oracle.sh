#!/bin/bash
# wait-for-oracle.sh

set -e

shift
cmd="$@"
sql="
whenever sqlerror exit 1;
connect system/oracle
select 1 from dual;
exit 0;
"

status="1"
while [ "$status" != "0" ]
do
  >&2 echo "Oracle is unavailable - sleeping"
  sleep 1
  sqlplus /nolog $sql
  status=$?
done

>&2 echo "Oracle is up - executing command"
exec $cmd
