#!/bin/sh

SCHEMA=$(cat <<EOF
DROP SCHEMA IF EXISTS temp_zip CASCADE;
CREATE SCHEMA temp_zip;

EOF
)


# remove MySQL stuff
RAW=$(wget -q -O - https://raw.githubusercontent.com/amitavmohanty/US-Zip-codes-Postal-codes/master/us.sql | \
  awk '!/^SET/{print}' | \
  sed 's/int(10).*/bigint,/; s/tinyint(.*)/int/; s/double(/numeric/; s/`us`/temp_zip.us/; s/ENGINE.*/;/; s/`//g;'
)
mkdir -p data
echo "$SCHEMA" "$RAW" > data/us_zipcodes.sql
