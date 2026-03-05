import os
import glob
from google import genai
from google.genai import types

from get_image import get_schedules_for_next_days

def get_gemini_token():
    try:
        with open("GEMINI_TOKEN", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ no GEMINI_TOKEN in current directory")
        return None

def generate_all_schedules_json():
    print("\n=== STAGE 1: Checkup and downloading the photos ===")
    get_schedules_for_next_days(days_ahead=10)
    png_files = glob.glob("*.png")
    if not png_files:
        print("no schedule photos")
        return

    api_key = get_gemini_token()
    if not api_key:
        return
        
    client = genai.Client(api_key=api_key)
    model = "gemini-3.1-flash-lite-preview"
    
    prompt = (
        'Ты умный парсер расписания уроков. '
        'Внимательно изучи прикрепленную фотографию школьного расписания. '
        'Переведи все данные из нее в строгий формат JSON. '
        'Примерная структура: ключами должны быть названия классов (например "10а") - буквы русские, маленькие, '
        'а значениями - списки уроков, где указан номер урока, название предмета и кабинет.'
        'пример: {"10а":[{"lesson_number": 1, "subject": "Физкультура", "classroom": "0.0"}]}'
        'другие расписания могут находиться в кадре, нужно только основное'
    )

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1, 
    )

    print("\n=== STAGE 2: LLM processing where needed ===")
    
    for image_filename in png_files:
        base_name = os.path.splitext(image_filename)[0]
        json_filename = f"{base_name}.json"
        
        # Если такой JSON уже лежит в папке, пропускаем
        if os.path.exists(json_filename):
            print(f"😎 file {json_filename} already exists.")

        print(f"\n[Using Gemini] processing the file: {image_filename}")
        
        with open(image_filename, "rb") as f:
            image_data = f.read()

        contents =[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=image_data, mime_type="image/png"),
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]

        print(f"🧠 processing the file with {model}...")
        
        try:
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.text is not None:
                    response_text += chunk.text
                
            # Сохраняем результат
            with open(json_filename, "w", encoding="utf-8") as f:
                f.write(response_text)
                
            print(f"✅ saved {json_filename}")
        except Exception as e:
            print(f"❌ error processing {image_filename}: {e}")

if __name__ == "__main__":
    generate_all_schedules_json()
