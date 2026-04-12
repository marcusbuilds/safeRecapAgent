# safeRecap

`safeRecap` is a FastAPI prototype for meeting summarization with local term redaction and post-processing rules before results are returned.

- Sanitizes configured forbidden terms before sending transcript content to the configured LLM provider
- Applies local redaction and rule enforcement to returned summaries and action items
- Supports OpenAI or Google Gemini via environment variables

`safeRecap` is a privacy-first meeting summarization app 
---

