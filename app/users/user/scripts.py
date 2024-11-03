import requests
import json
import re


# Script for checking the validity of the analogy
async def is_valid_analogy(analogy: str) -> bool:
    parts = analogy.split(':')

    if len(parts) != 2:
        return False

    word1 = parts[0].strip()
    word2 = parts[1].strip()

    return bool(word1) and bool(word2)


# Request to check the spelling of Kyrgyz words
async def is_kyrgyz_words(analogy: str) -> bool:
    url = "https://tamgasoft.kg/orfo/json.php"

    # Request headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://tamgasoft.kg/orfo/index.php?mode=word",
        "Origin": "https://tamgasoft.kg",
    }

    # Регулярное выражение для нахождения кириллических слов с учётом разделителей : - и пробелов
    words = re.findall(r'[а-яА-ЯёЁөӨңҢүҮ]+', analogy)

    for word in words:
        # Данные для отправки
        data = {
            "jsonData": f'{{"word":"{word}","method":"checkWord"}}'  # Формат данных как строка JSON
        }

        # Отправка POST-запроса
        response = requests.post(url, headers=headers, data=data)

        # Проверка и вывод результата
        if response.status_code == 200:
            result = response.json()  # Попытка разобрать ответ как JSON
            if result == 0:  # Предполагаем, что JSON содержит поле 'success'
                return False
        else:
            return False

    return True


async def is_kyrgyz_sentence(sentence):
    url = "https://tamgasoft.kg/orfo/tinymce/jscripts/tiny_mce/plugins/spellchecker/rpc.php"

    # Разделяем предложение на слова с учетом кириллических букв
    words = re.findall(r'[а-яА-ЯёЁөӨңҢүҮ]+', sentence)
    if not words:
        return "Нет слов для проверки."

    # Данные для отправки
    data = {
        "id": "c0",
        "method": "checkWords",
        "params": ["ky", words]
    }

    # Заголовки для запроса
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://tamgasoft.kg/orfo/index.php?mode=text",
    }

    # Отправка POST-запроса
    response = requests.post(url, headers=headers, json=data)

    # Проверка и вывод результата
    if response.status_code == 200:
        try:
            result = response.json()
            # Получаем список ошибочных слов
            incorrect_words = result.get("result", [])
            if "NO_ERROR" in incorrect_words:
                return "Туура"  # Все слова правильные
            elif incorrect_words:  # Если есть другие ошибки
                return "Бул сөздөр туура эмес жазылган: " + ", ".join(incorrect_words)
            else:
                return "Туура"  # Все слова правильные
        except json.JSONDecodeError:
            return "Ответ не в формате JSON."
    else:
        return f"Ошибка при запросе: {response.status_code}"
