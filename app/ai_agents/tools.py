
from langchain_core.tools import tool
import os

# save summary to file
@tool
def save_summary_to_file(summary: str, filename: str = "summary.txt") -> str:
    """Saves the summary to a text file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(summary)
        return f"Summary saved to {filename}"
    except Exception as e:
        return f"Failed to save summary: {e}"
