import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from get_schedule import generate_all_schedules_json
from get_data_for_calendar import get_data_for_calendar

SCOPES =['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """auntification stuff"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("Не найден credentials.json!")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def get_existing_events(service, day_date):
    start_of_day = day_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    end_of_day = day_date.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items',[])
    except HttpError as error:
        print(f'Error getting events: {error}')
        return[]

def main():
    generate_all_schedules_json()
    print("\n=== STAGE 3: Adding the events to Google Calendar ===")
    service = authenticate_google_calendar()
    today = datetime.datetime.now()
    for i in range(11):
        target_day = today + datetime.timedelta(days=i)
        day_str = target_day.strftime("%d.%m.%Y")
        new_events = get_data_for_calendar(cl="11т", day=target_day)
        if not new_events:
            continue
        print(f"\n--- {day_str} schedule processing ---")
        existing_events = get_existing_events(service, target_day)
        existing_keys =[]
        for ev in existing_events:
            summary = ev.get('summary', '')
            start_time = ev.get('start', {}).get('dateTime', '')
            existing_keys.append(f"{summary}_{start_time}")
        for event in new_events:
            event_summary = event.get('summary')
            event_start_time = event['start']['dateTime']
            
            is_duplicate = False
            for ex_key in existing_keys:
                if event_summary in ex_key and event_start_time in ex_key:
                    is_duplicate = True
                    break
            if is_duplicate:
                print(f"[-] Skip: '{event_summary}' в {event_start_time} (уже есть)")
            else:
                try:
                    created_event = service.events().insert(calendarId='primary', body=event).execute()
                    print(f"[+] Added: '{event_summary}'")
                except HttpError as error:
                    print(f"[!] Error adding '{event_summary}': {error}")
                    
    print("\n✅ Syncronized successfully")

if __name__ == '__main__':
    main()
