import requests
import re
from datetime import datetime, timedelta


try:
    with open("VK_TOKEN", "r") as f:
        VK_TOKEN = f.readline().strip()
except FileNotFoundError:
    print("no VK_TOKEN in current directory")
    exit(1)

DOMAIN = 'ulg_timetable'
API_VERSION = '5.131'


MONTHS = {
    'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
    'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
}

def get_schedules_for_next_days(days_ahead=10):
    url = 'https://api.vk.com/method/wall.get'
    params = {
        'domain': DOMAIN,
        'count': 50,  
        'access_token': VK_TOKEN,
        'v': API_VERSION
    }
    
    response = requests.get(url, params=params).json()
    if 'error' in response:
        print(f"VK API error: {response['error']['error_msg']}")
        return
    posts = response['response']['items']
    today = datetime.now().date()
    target_dates = {}
    for i in range(days_ahead + 1): 
        d = today + timedelta(days=i)
        
        target_dates[(d.day, d.month)] = d
    downloaded_dates = set()
    for post in posts:
        text = post.get('text', '')
        match = re.search(r'(\d{1,2})\s*([а-яА-Я]+)', text)
        if match:
            day = int(match.group(1))
            month_str = match.group(2).lower()
            if month_str in MONTHS:
                month = MONTHS[month_str]
                if (day, month) in target_dates:
                    if (day, month) in downloaded_dates:
                        continue
                    target_date = target_dates[(day, month)]
                    year = target_date.year
                    attachments = post.get('attachments',[])
                    for att in attachments:
                        if att['type'] == 'photo':
                            sizes = att['photo']['sizes']
                            best_photo = max(sizes, key=lambda s: s['width'] * s['height'])
                            photo_url = best_photo['url']
                            filename = f"{day:02d}.{month:02d}.{year}.png"
                            download_photo(photo_url, filename)
                            downloaded_dates.add((day, month))
                            break 
    
    print("\n=== Download report ===")
    for (d, m), date_obj in target_dates.items():
        date_str = date_obj.strftime("%d.%m.%Y")
        if (d, m) in downloaded_dates:
            print(f"✅ {date_str}")
        else:
            print(f"❌ {date_str}")

def download_photo(url, filename):
    print(f"Found the schedule. downloading the file: {filename}...")
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(f"cached/{filename}", 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

if __name__ == "__main__":
    get_schedules_for_next_days(days_ahead=10)
