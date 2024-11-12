import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
client.api_key = os.getenv('OPENAI_API_KEY')

async def get_chatgpt_response(prompt: str) -> str:
    """
    Функция принимает текстовый промпт, отправляет его в ChatGPT, и возвращает ответ.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )
        answer = response.choices[0].message.content
        return answer.strip()

    except Exception as e:
        print(f"Ошибка при запросе к ChatGPT: {e}")
        return "Произошла ошибка при получении ответа от ChatGPT."
