"""
Bitwarden Splunk App
"""
import asyncio
import aiohttp
import json
import argparse
import base64
import hashlib
import os
import subprocess
import shutil
import datetime
from pyModels.EventLogModel import EventLogModel
from pyModels.EventResponseModel import EventResponseModel

argparser = argparse.ArgumentParser()
argparser.add_argument(
    '--password',
    help='Bitwarden master password',
    required=True
)
argparser.add_argument(
    '--id',
    help='Bitwarden client ID',
    required=True
)
argparser.add_argument(
    '--secret',
    help='Bitwarden client secret',
    required=True
)
argparser.add_argument(
    '--events',
    help='Log events',
    default=False,
    action='store_true'
)
argparser.add_argument(
    '--groups',
    help='Log groups',
    default=False,
    action='store_true'
)
argparser.add_argument(
    '--collections',
    help='Log collections',
    default=False,
    action='store_true'
)
argparser.add_argument(
    '--stdout',
    help='Print logs to stdout',
    default=True,
    action='store_true'
)
argparser.add_argument(
    '--debug',
    help='Enable debug logging',
    default=False,
    action='store_true'
)

args = argparser.parse_args()

BW_BASE_URL = os.getenv("BW_BASE_URL", "https://vault.bitwarden.com")
BW_API_URL = os.getenv("BW_API_URL", "https://api.bitwarden.com")
BW_IDENTITY_URL = os.getenv(
    "BW_IDENTITY_URL", "https://identity.bitwarden.com")
BW_CLIENT_ID = args.id or os.getenv("BW_CLIENT_ID")
BW_PASSWORD = args.password or os.getenv("BW_PASSWORD")
BW_CLIENT_SECRET = args.secret or os.getenv("BW_CLIENT_SECRET")
BW_CLI_SYNC_INTERVAL = 1 * 60  # 1 minute
EVENTS_START_DATE = (datetime.datetime.now() -
                     datetime.timedelta(days=365)).isoformat()
SPLUNK_API_URL = os.getenv("SPLUNK_API_URL", "http://192.168.1.11:8089")
DEBUG = args.debug

async def bw_authenticate():
    payload = 'client_id=' + BW_CLIENT_ID + '&client_secret=' + \
        BW_CLIENT_SECRET + '&grant_type=client_credentials&scope=api.organization'

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}

    async with aiohttp.ClientSession() as session:
        async with session.post(BW_BASE_URL + "/identity/connect/token", headers=headers, data=payload) as response:
            response.raise_for_status()
            response_json = await response.json()
            return response_json['access_token']

def get_cli_session_key():
    if not shutil.which('bw'):
        raise Exception('Bitwarden CLI is not installed')

    if not BW_PASSWORD:
        raise Exception('BW_PASSWORD was not set')

    bw_session = subprocess.run(
        ['bw', 'unlock', BW_PASSWORD, '--raw'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True
    )

    if bw_session.stderr:
        print(f'Error: {bw_session.stderr}')

    return bw_session.stdout.strip()

def bw_decrypt_names(object_type):
    try:
        session_key = get_cli_session_key()
    except Exception as e:
        print(f'Error: {e}')
        return {}

    bw_status = subprocess.run(['bw', 'status'], capture_output=True)
    bw_status = json.loads(bw_status.stdout)
    last_sync = datetime.datetime.strptime(
        bw_status['lastSync'], '%Y-%m-%dT%H:%M:%S.%fZ')
    if (datetime.datetime.now() - last_sync).total_seconds() > BW_CLI_SYNC_INTERVAL:
        subprocess.run(['bw', 'sync'], stdout=subprocess.DEVNULL)
    object_list = subprocess.run(
        ['bw', 'list', object_type, '--session', session_key], capture_output=True)
    object_list = json.loads(object_list.stdout)

    # create dictionary of itemIds to itemNames
    object_name_map = {}
    for object in object_list:
        object_name_map[object['id']] = object['name']

    return object_name_map

def hash_data(data):
    event_hash = hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True).encode()).digest()

    event_hash_b64 = base64.b64encode(event_hash).decode()

    data['hash'] = event_hash_b64
    return data

async def bw_get_events(token, to_stdout):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    params = {
        'startDate': EVENTS_START_DATE
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'{BW_API_URL}/public/events',
                headers=headers,
                params=params) as response:
            response.raise_for_status()
            event_response = EventResponseModel(**await response.json())
            events = event_response.data
            events = [dict((k, v) for k, v in event.items() if v is not None)
                      for event in events]  # remove null values

            if shutil.which('bw'):
                item_name_map = bw_decrypt_names('items')
                collection_name_map = bw_decrypt_names('collections')

                for event in events:
                    if 1100 <= event['type'] <= 1199:
                        event['name'] = item_name_map.get(event['itemId'], '')
                    if 1300 <= event['type'] <= 1399:
                        event['name'] = collection_name_map.get(
                            event['collectionId'], '')
                    hash_data(event)
            else:
                for event in events:
                    if 1100 <= event['type'] <= 1199:
                        event['name'] = 'Cannot decrypt name. Bitwarden CLI not found.'
                    if 1300 <= event['type'] <= 1399:
                        event['name'] = 'Cannot decrypt name. Bitwarden CLI not found.'
                    hash_data(event)

            if to_stdout:
                print(json.dumps(events, indent=2))

            return events

async def main():

    if args.events:
        token = bw_authenticate()
        events = await bw_get_events(token, args.stdout)

if __name__ == '__main__':
    asyncio.run(main())
