#!/bin/bash
BASEDIR="/opt/devops/script/telegram-script"
SHEET_ID="$file_Id"
JSON_KEY_FILE="${BASEDIR}/${your_google_service_account}.json"
TOKEN_URI="https://oauth2.googleapis.com/token"
 
CLIENT_EMAIL=$(jq -r '.client_email' < "$JSON_KEY_FILE")
PRIVATE_KEY=$(jq -r '.private_key' < "$JSON_KEY_FILE")
 
echo "$PRIVATE_KEY" > /tmp/private_key.pem
 
header=$(echo -n '{"alg":"RS256","typ":"JWT"}' | openssl base64 -e | tr -d '\n=' | tr '/+' '_-' )
claim=$(echo -n "{\"iss\":\"$CLIENT_EMAIL\",\"scope\":\"https://www.googleapis.com/auth/spreadsheets.readonly\",\"aud\":\"$TOKEN_URI\",\"exp\":$(($(date +%s)+3600)),\"iat\":$(date +%s)}" | openssl base64 -e | tr -d '\n=' | tr '/+' '_-' )
signature=$(echo -n "$header.$claim" | openssl dgst -sha256 -sign /tmp/private_key.pem | openssl base64 -e | tr -d '\n=' | tr '/+' '_-' )
jwt="$header.$claim.$signature"
 
ACCESS_TOKEN=$(curl -s --request POST "$TOKEN_URI" \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=$jwt" | jq -r .access_token)
 
rm /tmp/private_key.pem
 
 
WEB="官網主域名"
APP="APP輪替域名"
RANGE_WEB="'$WEB'!A5:C7"
RANGE_APP="'$APP'!A7:C10"
 
fetch_data() {
  local range=$1
  local response=$(curl -s --request GET \
    "https://sheets.googleapis.com/v4/spreadsheets/$SHEET_ID/values/$range" \
    --header "Authorization: Bearer $ACCESS_TOKEN")
 
  echo "$response" | jq -r '.values[] | @tsv' | awk -F'\t' '{print $1 "\t\t" $3}'
}
 
echo "${WEB}:"
fetch_data "$RANGE_WEB"
echo ""
echo "${APP}:"                                                                                                     
fetch_data "$RANGE_APP"
