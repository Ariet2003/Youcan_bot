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

# Script for spell checking Kyrgyz words
async def is_kyrgyz_words(analogy: str) -> bool:
    url = "https://tamgasoft.kg/orfo/json.php"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://tamgasoft.kg/orfo/index.php?mode=word",
        "Origin": "https://tamgasoft.kg",
    }

    words = re.findall(r'[а-яА-ЯёЁөӨңҢүҮ]+', analogy)

    for word in words:
        data = {
            "jsonData": f'{{"word":"{word.lower()}","method":"checkWord"}}'  # Формат данных как строка JSON
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            result = response.json()
            if result == 0:
                return False
        else:
            return False
    return True

# # Script for spell checking Kyrgyz sentences
async def is_kyrgyz_sentence(sentence):
    url = "https://tamgasoft.kg/orfo/tinymce/jscripts/tiny_mce/plugins/spellchecker/rpc.php"

    words = [word.lower() for word in re.findall(r'[а-яА-ЯёЁөӨңҢүҮ]+', sentence)]
    if not words:
        return "Сөз жазылган жок"

    data = {
        "id": "c0",
        "method": "checkWords",
        "params": ["ky", words]
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://tamgasoft.kg/orfo/index.php?mode=text",
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            result = response.json()
            incorrect_words = result.get("result", [])
            if "NO_ERROR" in incorrect_words:
                return "Туура"
            elif incorrect_words:
                return "Бул сөздөр туура эмес жазылган: " + ", ".join(incorrect_words)
            else:
                return "Туура"
        except json.JSONDecodeError:
            return "Жооп JSON форматында эмес."
    else:
        return f"Боттон ката кетти: {response.status_code}"

# Script for spell checking Russian words
async def is_russian_words(analogy: str) -> bool:
    words = re.split(r'[:\- ]+', analogy)

    url = "https://speller.yandex.net/services/spellservice.json/checkText"

    for word in words:
        if not word:
            continue

        params = {
            "text": word,
            "lang": "ru",
            "options": 0,
            "format": "plain"
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            errors = response.json()
            if errors:
                return False
        else:
            return False
    return True

# Script for spell checking Russian sentence
async def is_russian_sentence(sentence):
    params = {
        "text": sentence,
        "lang": "ru",
        "options": 0,
        "format": "plain"
    }

    url = "https://speller.yandex.net/services/spellservice.json/checkText"

    response = requests.get(url, params=params)

    if response.status_code == 200:
        errors = response.json()
        if errors:
            for error in errors:
               return f"Неправильное слово: {error['word']}"
        else:
            return "Правильно"
    else:
        return f"Ошибка при выполнении запроса: {response.status_code}"