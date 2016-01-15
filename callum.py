# /usr/bin/python3

import httplib2
import os

from apiclient import discovery
from apiclient.errors import HttpError

import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
import json

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'callum_cred.json'
APPLICATION_NAME = 'callum'
MERGE_CAL_NAME = 'callum-merged'

calmn_list = ['Theatre', 'Class', 'Lab', 'Work', 'Misc.']


def get_credentials():
    """
    gets credentials.
    returns Credentials.
    """

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'callum_usercred.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print ('Storing credentials to ' + credential_path)
    return credentials


def get_mergecal(service, calendars):
    """
    returns the calendar object of the jack-merged calendar,
    creating the calendar if necessary
    """
    if not any(cal['summary'] == 'jack-merged' for cal in calendars['items']):
        # create merge calendar
        ncal = {
            'summary': 'jack-merged',
            'timeZone': [cal for cal in calendars['items'] if 'primary' in cal][0]['timeZone']
        }
        return service.calendars().insert(body=ncal).execute()
    else:
        calId = [cal for cal in calendars['items'] if cal['summary'] == 'jack-merged'][0]['id']
        return service.calendars().get(calendarId=calId).execute()


def get_evts(service, calId):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    evtsRes = service.events().list(calendarId=calId, timeMin=now).execute()
    return evtsRes.get('items', [])


def clear_cal(service, calId):
    for evt in get_evts(service, calId):
        try:
            service.events().delete(calendarId=calId, eventId=evt['id']).execute()
        except HttpError:
            continue


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    cals = service.calendarList().list(pageToken=None).execute()

# get and clear merge calendar
    merge_cal = get_mergecal(service, cals)
    clear_cal(service, merge_cal['id'])

# re-load merge calendar
    calm_list = [cal for cal in cals['items'] if cal['summary'] in calmn_list]
    for cal in calm_list:
        evts = get_evts(service, cal['id'])
        for evt in evts:
            if evt['status'] == 'cancelled':
                continue
            elif evt['status'] == 'confirmed':
                n_evt = {
                    'start': evt['start'],
                    'end': evt['end'],
                    'summary': evt['summary']
                }
                if 'recurrence' in evt:
                    n_evt['recurrence'] = evt['recurrence']
                service.events().insert(calendarId=merge_cal['id'], body=n_evt).execute()

# watch loop



if __name__ == "__main__":
    main()
