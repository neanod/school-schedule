from pathlib import Path
import datetime
import json

times = {
    1:["9:15", "10:50"],
    2:["11:00", "13:00"],
    3: ["13:10", "14:45"],
}

def get_data_for_calendar(cl="11т", day=None):
    if day is None:
        day = datetime.datetime.now()
        
    current_date: str = day.strftime("%d.%m.%Y")
    current_date_formated: str = day.strftime("%Y-%m-%d")
    needed_name = f"{current_date}.json"
    
    if not Path(f"cached/{needed_name}").exists():
        return[]
        
    with open(f"cached/{needed_name}", "r", encoding="utf8") as f:
        schedule_raw = f.read()
        
    
    schedule_raw = schedule_raw.replace("```json", "").replace("```", "").strip()
    try:
        schedule_json: dict[str, list[dict[str, str|int]]] = json.loads(schedule_raw)
    except json.JSONDecodeError:
        
        try:
            schedule_json = eval(schedule_raw)
        except Exception as e:
            raise ValueError(f"cant read JSON from {needed_name}: {e}")
    schedule_cl = schedule_json.get(cl)
    if not schedule_cl:
        return[]
        
    events: list[dict[str, str|dict[str, str]]] =[]
    for lesson in schedule_cl:
        try:
            assert "subject" in lesson.keys()
            assert "lesson_number" in lesson.keys()
            assert "classroom" in lesson.keys()
        except AssertionError:
            raise ValueError(f"Incorrect JSON format in {needed_name}")
            
        lesson_num = int(lesson['lesson_number'])
        
        if lesson_num not in times:
            continue
            
        ev = {
            "summary": str(lesson.get("subject")),
            "location": f"Classroom {lesson.get('classroom')}",
            "description": f"",
            "start": {
                "dateTime": f"{current_date_formated}T{times[lesson_num][0]}:00",
                "timeZone": "Europe/Moscow",
            },
            "end": {
                "dateTime": f"{current_date_formated}T{times[lesson_num][1]}:00",
                "timeZone": "Europe/Moscow",
            },
            "reminders": {
                "useDefault": False,
                "overrides":[],
            },
        }
        events.append(ev)
    return events
