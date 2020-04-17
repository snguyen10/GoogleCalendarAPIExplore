from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from datetime import datetime, timedelta
import datefinder
import sys


def get_credentials():
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
    credentials = flow.run_console()
    pickle.dump(credentials, open("token.pk1", "wb"))
    credentials = pickle.load(open("token.pk1", "rb"))
    return credentials


def get_calendar_service():

    try:
        credentials = pickle.load(open("token.pk1", "rb"))
    except FileNotFoundError:
        credentials = get_credentials()
    service = build("calendar", "v3", credentials=credentials)
    return service


def create_event(service, start_time_str, summary, duration=1, description=None, location=None):

    matches = list(datefinder.find_dates(start_time_str))
    if len(matches):
        start_time = matches[0]
        end_time = start_time + timedelta(hours=duration)

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'America/New_York',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    print(summary + " created successfully")
    return service.events().insert(calendarId='primary', body=event).execute()


def get_first_event(service):
    result = service.calendarList().list().execute()
    calendar_id = result['items'][0]['id']
    result = service.events().list(calendarId=calendar_id, timeZone="America/New_York").execute()
    print(result['items'][0])


def main():
    service = get_calendar_service()
    summary = sys.argv[1]
    start_time = sys.argv[2]
    duration = int(sys.argv[3])
    create_event(service, start_time, summary, duration)


if __name__ == "__main__":
    main()
