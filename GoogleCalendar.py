import os.path
import datetime as dt

from google.auth.transport.requests import  Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    # Credentials for logging into your google account
    creds = None
    # if token exists, then cred = token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # if the creds do not exist, or are invalid, t
    if not creds or not creds.valid:
        
        # if creds are expired, refresh them. This does not work for now. Idk why
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # if the creds do not exist, then create them
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        # We are using the google calendar
        service = build('calendar', 'v3', credentials=creds)

        # The time now
        now = dt.datetime.now().isoformat() + 'Z'

        # Before we get the events, we first need to get all of the users calendars
        # This gets the users calendars:
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        
        calendar_ids = []
        for calendar in calendar_list['items']:
            calendar_ids.append(calendar['id'])
        events = []
        for calendar in calendar_ids:
            event_result = service.events().list(
                calendarId = calendar,
                timeMin = now, 
                maxResults = 10,
                singleEvents = True, 
                orderBy = 'startTime'
            ).execute()
            events.append(event_result)

        if not events:
            print('No upcoming events found.')
            return
        
        for event in event_result.get('items', []):
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            print(start, end)
    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()