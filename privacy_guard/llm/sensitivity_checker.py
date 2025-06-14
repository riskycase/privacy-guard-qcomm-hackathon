import requests
from privacy_guard.config import API_TOKEN

class SensitivityChecker:
    def __init__(self, llm_url: str = "http://localhost:3001/api/v1/openai/chat/completions"):
        self.llm_url = llm_url

    def is_sensitive(self, dom: str, url: str) -> bool:
        system_prompt = (
            "You are a helpful assistant that determines if web content is sensitive. "
            "If the content contains personal, financial, or confidential information, answer 'yes'. "
            "Otherwise, answer 'no'. Respond with only 'yes' or 'no'."
        )
        user_prompt = (
            f"URL: {url}\n"
            f"Content: {dom[:2000]}\n"  # Truncate to 2000 chars for 3B model
            "Is the content sensitive?"
        )
        payload = {
            "model": "gpt-3b",  # adjust if needed
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 2,
            "temperature": 0.0
        }
        try:
            headers = {}
            if API_TOKEN:
                headers['Authorization'] = f'Bearer {API_TOKEN}'
            
            response = requests.post(self.llm_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"].strip().lower()
            return answer.startswith("y")
        except Exception:
            return False
