import json
import os

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "leak_detected": {"type": "boolean"},
        "leak_volume":   {"type": "string"},
        "leak_object":   {"type": "string"},
        "company":       {"type": "string"},
        "details":       {"type": "string"}
    },
    "required": ["leak_detected", "leak_object", "company"]
}

SYSTEM_PROMPT = """
Ты эксперт по информационной безопасности. Анализируй сообщение и верни JSON с полями:
- leak_detected (boolean): true, если сообщение содержит признаки утечки данных, иначе false.
- leak_volume (string): объём утечки (кол-во записей, размер и т.п.). Пусто, если утечки нет.
- leak_object (string): что именно утекло (например: база клиентов, пароли и т.д.). Пусто, если утечки нет.
- company (string): организация, к которой относится утечка. Пусто, если неизвестна или утечки нет.
- details (string): доп. сведения, например, ссылки, формат файлов, реакция аудитории. Пусто, если утечки нет.
Если утечки нет (leak_detected: false), все остальные поля должны быть пустыми строками ("").
Формат ответа — строго валидный JSON.
""".strip()


api_key = os.environ.get('API_KEY')
client = OpenAI(api_key=api_key)


def analyze_message(text: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Анализируй сообщение: «{text}»"}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "leak_analysis",
                    "schema": JSON_SCHEMA
                }
            }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "leak_detected": False,
            "leak_volume":   "",
            "leak_object":   "",
            "company":       "",
            "details":       f"Error: {e}"
        }
