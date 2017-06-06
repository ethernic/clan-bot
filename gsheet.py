from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import datetime
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import pickle
import pprint

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'clan-bot'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def make_sheet(service, page, spreadsheet_id):
    requests = []
    requests.append({'addSheet': {'properties': {'title': page}}})
    body = {'requests': requests}
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    return response['replies'][0]['addSheet']['properties']['sheetId']

def insert_data(service, page, spreadsheet_id):
    top_row = ['PSN', 'Days', 'Member Since', 'Days', 'Last Played']
    with open ('pickle.txt', 'rb') as pf:
        values = pickle.load(pf)
    values.insert(0, top_row)
    range_name = page
    value_input_option = 'USER_ENTERED'
    body = {'values': values}
    result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption=value_input_option, body=body).execute()

def format_data(service, sheet_id, spreadsheet_id):
    requests = []
    body = {
                "requests": [
                    { 
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": sheet_id,
                                "gridProperties": {
                                    "frozenRowCount":1
                                }
                            },
                            "fields": "gridProperties.frozenRowCount"
                        }
                    },
                    {
                        "autoResizeDimensions": {
                            "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 5
                            }
                        }
                    }
                ]
        }
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    service = discovery.build('sheets', 'v4', credentials=credentials)
    spreadsheet_id = '1DIdDsAgMpIGw7kIkxZ_O1QgS_FaH8IPo2imVIukAs48'
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    sheet_id = make_sheet(service, today, spreadsheet_id)
    print(sheet_id)
    insert_data(service, today, spreadsheet_id)
    format_data(service, sheet_id, spreadsheet_id)
    
    #response = request.execute()

    # TODO: Change code below to process the `response` dict:
    #print(response)


if __name__ == '__main__':
    main()