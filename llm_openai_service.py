from openai import OpenAI
from config import Config

# Инициализация клиента с API ключом
client = OpenAI(api_key=Config.OPENAI_API_KEY)

def generate_comment(system_prompt: str, user_prompt: str) -> str:
    """Генерация комментария через OpenAI Chat API."""
    if not Config.OPENAI_API_KEY:
        return "Ошибка: API ключ OpenAI не установлен."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",  # Можно заменить на "gpt-4"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при генерации комментария через OpenAI: {e}"
