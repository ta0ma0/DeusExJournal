import openai
from config import Config
from openai import OpenAI
client = OpenAI()

if Config.OPENAI_API_KEY:
    openai.api_key = Config.OPENAI_API_KEY

def generate_comment(system_prompt: str, user_prompt: str) -> str:
    """Generates a comment using OpenAI's API."""
    if not Config.OPENAI_API_KEY:
        return "Ошибка: API ключ OpenAI не установлен."

    try:
        response = client.responses.create(
            model="gpt-3.5-turbo",  # Вы можете выбрать другую модель, например, "gpt-4"
            instructions = system_prompt,
            input = user_prompt,
        )
        print(model)
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при генерации комментария через OpenAI: {e}"