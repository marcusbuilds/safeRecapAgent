# safeRecap

`safeRecap` is a FastAPI prototype for meeting summarization with local term redaction and post-processing rules before results are returned.

- Sanitizes configured forbidden terms before sending transcript content to the configured LLM provider
- Applies local redaction and rule enforcement to returned summaries and action items
- Supports OpenAI or Google Gemini via environment variables
- Can protect API routes with `X-API-Key` when `APP_API_KEY` is configured

`safeRecap` is a privacy-first meeting summarization app for enterprise and regulated environments (LegalTech, FinTech, and compliance-heavy workflows).

---

## 🚀 Features

### **Hybrid AI Pipeline**

- Forbidden terms are masked before transcript content is sent to the external LLM
- Local rules are applied after generation before the response is returned
- Prompt contents and API key fragments are not logged by the backend
- Use `APP_API_KEY` to require `X-API-Key` on every request

### **Security-Oriented Design**

- Local redaction of forbidden terms
- Local rule engine for compliance enforcement
- Shared API-key protection is available for deployed environments
- Sensitive data still lives in memory in this prototype

### **Developer-Friendly**

- Clean FastAPI backend
- Easily swappable local rules engine
- Docker-ready configuration with env-file based secrets
- Includes unit tests and CI scaffolding

---

## 🧩 Architecture Overview

```
Client → FastAPI Backend
           │
           ├─ Local Filter Engine (sensitive data, rules)
           └─ OpenAI API (summary + action items)

Final Output = LLM summary/action items + local enforcement + redactions
```

---

## 📡 API Endpoints

### **POST /meetings/raw**

Upload non-sensitive, raw meeting notes.

```json
{
  "meeting_id": "optional-id",
  "text": "Meeting transcript or notes..."
}
```

### **POST /meetings/sensitive**

Upload sensitive terms and compliance rules.

```json
{
  "meeting_id": "abc-123",
  "forbidden_terms": ["SSN", "client-secret"],
  "rules": [
    {
      "id": "r1",
      "type": "remove_if_contains",
      "pattern": "external share"
    }
  ]
}
```

### **GET /meetings/{id}/summary**

Returns sanitized summary + action items.

```json
{
  "meeting_id": "abc-123",
  "result": {
    "summary": "...",
    "action_items": ["..."],
    "applied_rules": [...]
  }
}
```

When `APP_API_KEY` is set, include it as the `X-API-Key` request header on all endpoints.

---

## 🛠️ Setup

### **1. Clone the Repo**

```
git clone <your-repo>
cd safeRecap
```

### **2. Install Dependencies**

```
pip install -r requirements.txt
```


### **3. Create Your Env File**

Copy `.env.example` to `.env` for Docker or use `.env.example` as the starting point for local development, then fill in the values you need.

```env
POSTGRES_USER=""
POSTGRES_PASSWORD=""
POSTGRES_DB=""
DATABASE_URL=""
APP_ENCRYPTION_KEY=""
APP_API_KEY=""
LLM_PROVIDER="google"
OPENAI_API_KEY=""
GOOGLE_API_KEY=""
GOOGLE_GENAI_MODEL="gemini-2.0-flash-lite"
```

Notes:

* `APP_API_KEY` is optional for local development but should be set for any deployed environment.
* `DATABASE_URL` should point at your actual Postgres instance.
* Only set the API key for the provider selected by `LLM_PROVIDER`.

### **4. Run the Server**

```
uvicorn app.main:app --reload
```

Server runs at **[http://localhost:8000](http://localhost:8000)**.

---

## 📦 Docker

Create a local `.env` file first, then run:

```bash
docker compose up --build
```

---

## 🧪 Tests

Run included tests:

```
pytest -q
```

---

## 📜 Project Structure

```
app/
 ├─ main.py              # API layer
 ├─ filters.py           # Local filtering + sensitive enforcement
 ├─ openai_client.py     # OpenAI wrapper
 └─ ...
tests/
 └─ test_filters.py      # unit tests for filter engine
Dockerfile
requirements.txt
README.md
```

---

## 🛡️ Security Considerations

* This repo no longer includes hardcoded runtime secrets in tracked files, but any previously used credentials should still be rotated.
* Forbidden terms are masked before transcript content is sent to the external LLM.
* The service does not log prompts or API key fragments.
* If `APP_API_KEY` is unset, the API remains open for local use. Set it before exposing the service outside a trusted environment.
* Sensitive data is still stored in memory in this prototype. Use encrypted persistence before production use.

---

## 🧭 Future Enhancements

* Move meeting and policy data into encrypted database storage
* Add stronger authentication and authorization beyond a shared API key
* Add background processing for long transcripts
* Expand the local rule engine

---

## 📄 License

MIT — free to use for interviews, demos, or internal prototypes.

---

