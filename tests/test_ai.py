import sys
import os
# Ensure project root is in sys.path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
from app.ai_client import get_llm_client
import asyncio

# Load environment variables from .env.example if present
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env.example')
    load_dotenv(dotenv_path)
except ImportError:
    print('python-dotenv not installed; skipping .env.example loading')

async def main():
    client = get_llm_client()
    prompt = (
        'Answer the following question in JSON format with the keys: summary and action_items.\n'
        'Example:\n'
        '{"summary": "The sky is blue due to Rayleigh scattering.", "action_items": ["Read more about Rayleigh scattering", "Observe the sky on a clear day"]}\n'
        '\nQuestion: Why is the sky blue?'
    )
    response = await client.generate(prompt)
    print('Full response:', response)
    if isinstance(response, dict):
        if 'summary' in response:
            print('Summary:', response['summary'])
        else:
            print('Response dict:', response)
    else:
        print('Response:', response)

if __name__ == '__main__':
    asyncio.run(main())
