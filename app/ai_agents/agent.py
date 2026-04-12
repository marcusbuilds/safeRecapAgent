from typing import List

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from .tools import save_summary_to_file
from app.ai_client import get_llm_client

def run_agent(user_input: str, history: list) -> AIMessage:
    """Agent runner using get_llm_client() for summarization and save tool."""
    try:
        llm = get_llm_client()
        # For demo: if user asks to save a summary, extract and save it
        if user_input.lower().startswith("save the summary"):
            # Extract summary from input (simple heuristic)
            import re
            match = re.search(r"summary[:]? '?(.*?)'?($|\.)", user_input, re.IGNORECASE)
            summary = match.group(1) if match else "No summary provided."
            save_result = save_summary_to_file.invoke({"summary": summary, "filename": "summary.txt"})
            return AIMessage(content=save_result)
        # Otherwise, use LLM to summarize
        prompt = f"Summarize the following meeting in 1-2 sentences, focusing on key points only.\nMeeting: {user_input}"
        result = llm.generate(prompt=prompt)
        if hasattr(result, 'result'):
            summary = result['result'].get('summary', str(result))
        elif isinstance(result, dict) and 'summary' in result:
            summary = result['summary']
        else:
            summary = str(result)
        return AIMessage(content=summary)
    except Exception as e:
        return AIMessage(content=f"Error: {str(e)}\n\nPlease try rephrasing your request or provide more specific details.")
