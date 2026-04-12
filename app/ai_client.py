"""
# app/ai_client.py

"""

import os
import json
import asyncio
from typing import Any

import openai


class OpenAIClient:
    def __init__(self):
        self.api_key = os.environ['OPENAI_API_KEY']
        openai.api_key = self.api_key

    async def generate(self, prompt: str) -> dict:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.api_key)
        response = await client.chat.completions.create(
            model='gpt-4o',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=400,
            temperature=0.2
        )
        content = response.choices[0].message.content
        try:
            parsed = json.loads(content)
            return parsed
        except Exception:
            lines = content.splitlines()
            summary = lines[0] if lines else ''
            ais = [l.strip('-* ') for l in lines if l.strip().startswith(('-', '*'))]
            return {'summary': summary, 'action_items': ais}



# google-generativeai (Gemini) client
import google.generativeai as genai


class GoogleAIClient:
    def __init__(self):
        self.api_key = os.environ['GOOGLE_API_KEY']
        genai.configure(api_key=self.api_key)
        self.model_name = os.environ.get('GOOGLE_GENAI_MODEL')

    async def generate(self, prompt: str) -> dict:
        # google-generativeai is synchronous; run in thread executor for async compatibility
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate_sync, prompt)

    def _generate_sync(self, prompt: str) -> dict:
        import logging
        model = genai.GenerativeModel(self.model_name)
        try:
            response = model.generate_content(prompt, generation_config={
                'temperature': 0.2,
                'max_output_tokens': 400
            })
            if hasattr(response, 'text'):
                content = response.text
            else:
                content = str(response)
        except Exception as e:
            logging.error("Gemini API call failed")
            return {'error': 'Gemini API call failed'}

        if not content or content.strip() == '':
            logging.error("Gemini API returned no content")
            return {'error': 'Gemini API returned no content'}

        try:
            import re
            code_block_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
            if code_block_match:
                json_str = code_block_match.group(1)
            else:
                json_str = content
            parsed = json.loads(json_str)
            summary = parsed.get('summary')
            action_items = parsed.get('action_items')
            if (not summary and not action_items):
                logging.warning("Gemini API returned empty summary/action_items")
                return {'summary': summary or '', 'action_items': action_items or []}
            return parsed
        except Exception:
            lines = content.splitlines()
            summary = ''
            action_items = []
            for line in lines:
                if line.lower().startswith('summary:'):
                    summary = line.partition(':')[2].strip()
                elif line.lower().startswith('action items:'):
                    idx = lines.index(line) + 1
                    action_items = [l.strip('-* ') for l in lines[idx:] if l.strip()]
                    break
            logging.warning("Gemini API returned non-JSON content")
            return {'summary': summary, 'action_items': action_items}


# --- Factory for LLM Client ---
def get_llm_client():
    provider = os.environ.get('LLM_PROVIDER', 'google').lower()
    if provider == 'google':
        return GoogleAIClient()
    return OpenAIClient()
