import json
import re
from typing import Any

import requests

from app.config import get_settings

HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
FALLBACK_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
FALLBACK_MODEL_2 = "microsoft/Phi-3-mini-4k-instruct"


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self):
        self.settings = get_settings()
        self.provider = "huggingface"
        self.model_name = self.settings.hf_model or HF_MODEL
        print("USING HUGGINGFACE:", bool(self.settings.hf_api_key))
        print("MODEL:", self.model_name)

    def generate_with_hf(self, prompt: str, model: str | None = None) -> str:
        model_to_use = model or self.model_name
        headers = {}
        if self.settings.hf_api_key:
            headers["Authorization"] = f"Bearer {self.settings.hf_api_key}"

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 2000,
                "temperature": 0.7,
                "top_p": 0.92,
                "repetition_penalty": 1.15,
                "return_full_text": False,
            },
        }

        url = f"https://api-inference.huggingface.co/models/{model_to_use}"
        print(f"Calling HF API: {url}")
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=45,
        )

        print(f"HF Response Status: {response.status_code}")
        
        # Retry on 503 (model loading)
        if response.status_code == 503:
            print("Model loading, waiting 20 seconds...")
            import time
            time.sleep(20)
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=45,
            )

        if response.status_code != 200:
            error_text = response.text[:500]
            print(f"HF API Error: {error_text}")
            raise Exception(f"HF API failed with status {response.status_code}: {error_text}")
            raise Exception(f"HF API failed: {response.text}")

        data = response.json()

        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict) and "generated_text" in first:
                return str(first["generated_text"])

        raise Exception("Invalid HF response")

    def generate_json(self, messages: list[dict[str, str]], json_instruction: str) -> dict[str, Any]:
        try:
            prompt = self._messages_to_prompt(messages, json_instruction)
            raw = self.generate_with_hf(prompt)
            print("HF RAW:", raw[:300])

            # If empty string returned, try fallback model
            if not raw or not raw.strip():
                print("Empty response from primary model, trying fallback...")
                raw = self.generate_with_hf(prompt, model=FALLBACK_MODEL)

            match = re.search(r"{.*}", raw, re.DOTALL)
            if match:
                json_text = match.group(0)
            else:
                raise Exception("No JSON found in response")

            parsed = json.loads(json_text)

            # Ensure the response has the expected structure
            if isinstance(parsed, dict):
                # For product recommendations, ensure we have products array
                if "products" in parsed and not parsed["products"]:
                    # Retry once more with explicit instruction
                    retry_messages = messages + [
                        {"role": "system", "content": "CRITICAL: You MUST generate at least 3 realistic product recommendations. Do not return empty products array."}
                    ]
                    retry_prompt = self._messages_to_prompt(retry_messages, json_instruction)
                    raw = self.generate_with_hf(retry_prompt)
                    match = re.search(r"{.*}", raw, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group(0))

            return parsed
        except Exception as e:
            print(f"LLM generation failed: {e}")
            # Try fallback models
            for fallback_model in [FALLBACK_MODEL, FALLBACK_MODEL_2]:
                try:
                    print(f"Trying fallback model: {fallback_model}")
                    prompt = self._messages_to_prompt(messages, json_instruction)
                    raw = self.generate_with_hf(prompt, model=fallback_model)
                    match = re.search(r"{.*}", raw, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group(0))
                        if parsed.get("products"):  # Only return if we have products
                            return parsed
                except Exception as fallback_error:
                    print(f"Fallback model {fallback_model} failed: {fallback_error}")
                    continue

            # Return minimal structure without hardcoded products
            if "missing_fields" in json_instruction:
                return {
                    "category": "",
                    "budget": "",
                    "use_case": "",
                    "preferences": [],
                    "missing_fields": ["category", "budget", "use_case"],
                    "follow_up_questions": [
                        "What's your budget range?",
                        "What will you mainly use it for?",
                        "Which product category should I focus on?",
                    ],
                }

            # For product recommendations, return empty structure
            return {
                "reply": "I'd love to help you find the perfect products! Could you tell me more about what you're looking for?",
                "products": [],
                "follow_up_questions": [
                    "What's your budget?",
                    "What category are you interested in?",
                    "Any specific features you need?",
                ],
            }

    @staticmethod
    def _messages_to_prompt(messages: list[dict[str, str]], json_instruction: str) -> str:
        lines: list[str] = [
            "You are Shop AI, a friendly shopping assistant helping users find products on Indian e-commerce platforms.",
            "You MUST return ONLY valid JSON with product recommendations.",
            "No explanation outside JSON. No markdown formatting.",
            "",
            "Conversation history:",
        ]
        for message in messages:
            role = message.get("role", "user").upper()
            content = message.get("content", "")
            lines.append(f"{role}: {content}")
        lines.append("")
        lines.append("JSON Output Requirements:")
        lines.append(json_instruction)
        lines.append("")
        lines.append("Remember: Be conversational in your 'reply' field. Acknowledge what the user specifically asked for.")
        return "\n".join(lines)
