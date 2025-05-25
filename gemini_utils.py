import requests
import json
import re

def generate_gemini_response(api_key: str, prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    response_json = response.json()
    
    candidates = response_json.get("candidates", [])
    if not candidates:
        raise ValueError("No candidates in response")
    
    content = candidates[0].get("content", {})
    
    if "text" in content:
        return content["text"].strip()
    elif "parts" in content:
        parts = content["parts"]
        if isinstance(parts, list):
            return "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()
        else:
            return str(parts).strip()
    else:
        raise KeyError("No 'text' or 'parts' in content")

def analyze_with_gemini(report_text: str):
    api_key = os.getenv("API_KEY")   # hardcoded here
    
    prompt = f"""
You are a highly intelligent medical assistant AI. Analyze the following patient medical report and return a JSON response with the following fields:

1. **status** – Summarize the key health state of the patient. If any indicators (like blood pressure, sugar, etc.) are abnormal, explain briefly.
2. **suggestion** – Provide a recommendation such as whether the patient should consult a doctor, start medication, make lifestyle changes, or if the report is normal.
3. Try to identify any possible disease or medical issue from the report and include its condition (e.g., mild, moderate, critical).
4. If the report contains typos or poor OCR extraction, attempt to infer the correct medical meaning and provide a coherent analysis.
5. Return your output ONLY in raw JSON format.

Use this exact JSON structure for the response:

{{
  "status": "short summary of the medical condition",
  "suggestion": "clear and helpful medical advice"
}}

Here is the report text:

\"\"\" 
{report_text}
\"\"\"
"""
    raw_response = generate_gemini_response(api_key, prompt)
    
    # Remove markdown-style ```json ... ``` wrapper if present
    cleaned_response = re.sub(r"^```json\s*|\s*```$", "", raw_response, flags=re.DOTALL).strip()
    
    try:
        data = json.loads(cleaned_response)
        status = data.get("status", "No status found")
        suggestion = data.get("suggestion", "No suggestion found")
    except json.JSONDecodeError:
        status = "Parsing error"
        suggestion = raw_response
    
    return [status, suggestion]


if __name__ == "__main__":
    patient_report = """
    Patient has a blood pressure reading of 180/110, heart rate is elevated at 110 bpm.
    No signs of chest pain, but dizziness reported.
    """
    
    result = analyze_with_gemini(patient_report)
    print("Status:", result[0])
    print("Suggestion:", result[1])
