# Bitwarden Splunk App

A Splunk app for reporting Bitwarden event logs.

## Running the app

1. `pip3 install -r requirements.txt`
2. `export BW_PASSWORD="$(bw get password bitwarden)"` 
3. `./src/Splunk/program.py --id "<org-id>" --secret "<org-secret>" --password "<bw-pass>" --events`

Note: The `--password` argument is optional and is used to decrypt item and collection names from the event logs. The integration will still work without it, but the names will not be available.
