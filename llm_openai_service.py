import openai
from config import Config

if Config.OPENAI_API_KEY:
    openai.api_key = Config.OPENAI_API_KEY

def generate_comment(system_prompt: str, user_prompt: str) -> str:
    """Generates a comment using OpenAI's API."""
    if not Config.OPENAI_API_KEY:
        return "Ошибка: API ключ OpenAI не установлен."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-2024-08-06",  # Вы можете выбрать другую модель, например, "gpt-4"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка при генерации комментария через OpenAI: {e}"