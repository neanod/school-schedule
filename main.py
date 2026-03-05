import datetime
import os.path
import hashlib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from get_schedule import generate_all_schedules_json
from get_data_for_calendar import get_data_for_calendar

SCOPES = ['https://www.googleapis.com/auth/calendar']

def generate_event_id(summary, start_time_str):
    """
    Создает уникальный ID для события. 
    Google ID должен быть в base32 (строчные латинские буквы и цифры от 0 до 5).
    """
    # Создаем строку, которая уникально описывает урок (время + пометка школы)
    # Мы не берем summary, чтобы при замене предмета в то же время ID остался тем же
    unique_str = f"{start_time_str}_agl"
    # Хешируем и берем первые 20 символов (hex подходит под требования Google ID)
    event_id = hashlib.md5(unique_str.encode()).hexdigest()
    return event_id

def authenticate_google_calendar():
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

        for event in new_events:
            summary = event.get('summary', 'Урок')
            start_time = event['start'].get('dateTime')
            location = event.get('location', '')

            # Работаем только с уроками в АГЛ
            if "АГЛ" in location and start_time:
                # Генерируем уникальный ID для этого таймслота
                event['id'] = generate_event_id(summary, start_time)
                
                try:
                    # Используем insert. Если ID уже есть, Google выдаст ошибку 409
                    service.events().insert(calendarId='primary', body=event).execute()
                    print(f"[+] Added: '{summary}'")
                except HttpError as e:
                    if e.resp.status == 409:
                        # 409 Conflict означает, что событие с таким ID уже существует
                        print(f"[-] Skip: '{summary}' (слот в АГЛ уже занят)")
                    else:
                        print(f"[!] Error: {e}")
            else:
                # Если это не АГЛ, просто добавляем (или проигнорируй)
                try:
                    service.events().insert(calendarId='primary', body=event).execute()
                except HttpError as e:
                    print(f"[!] Error adding non-AGL event: {e}")

    print("\n✅ Synchronized successfully")

if __name__ == '__main__':
    main()
