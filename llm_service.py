import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)


def generate_comment(system_prompt: str, user_prompt: str) -> str:
    try:

        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_prompt
        )
        
        response = model.generate_content(
            contents=user_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=800,
                temperature=0.7,
                # top_p=0.9, 
                # top_k=40
            )
        )
        
        if response.prompt_feedback.block_reason:
            return f"Ошибка: Запрос был заблокирован по причине: {response.prompt_feedback.block_reason.name}"

        if response.candidates and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
        else:
            return "Ошибка: Не удалось сгенерировать комментарий (API вернул пустой ответ без объяснения причин)."

    except Exception as e:
        return f"Ошибка при генерации комментария: {e}"