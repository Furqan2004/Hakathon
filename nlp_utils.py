import requests
import json

def extract_columns_and_data(text: str) -> str:
    API_KEY = os.getenv("API_KEY")   # 🔐 Replace with your actual Gemini API key
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    prompt = (
        "Extract structured data from the following text and return it only in a clean key-value format, "
        "each pair on a new line like this:\n"
        '"key": "value"\n'
        '"key2": "value2"\n\n'
        f"Text:\n{text}"
    )

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        try:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "Error: Unexpected response structure from Gemini."
    else:
        return f"Error: {response.status_code} - {response.text}"
