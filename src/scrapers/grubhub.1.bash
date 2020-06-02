BEARER=$1
POINT=$2

BEARER_HEADER="authorization: Bearer $BEARER"
URL_POINT=${POINT/,/%20}
curl 'https://api-gtm.grubhub.com/auth' \
  -H 'authority: api-gtm.grubhub.com' \
  -H 'authorization: Bearer ded15766-2ed8-48a4-ba02-bb6607b4b44d' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37' \
  -H 'content-type: application/json;charset=UTF-8' \
  -H 'accept: */*' \
  -H 'origin: https://www.grubhub.com' \
  -H 'sec-fetch-site: same-site' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-dest: empty' \
  -H 'referer: https://www.grubhub.com/' \
  -H 'accept-language: en-US,en;q=0.9' \
  --data-binary '{"brand":"GRUBHUB","client_id":"beta_UmWlpstzQSFmocLy3h1UieYcVST","device_id":-1878585573,"refresh_token":"8a6260ee-1221-44b5-8c73-57c2db977d33"}' \
  --compressed
