# SHL Assessment Recommender Agent

A conversational AI agent that helps hiring managers find the right SHL assessments through natural language dialogue.

## What it does
- Clarifies vague hiring queries before recommending
- Recommends 1-10 SHL assessments based on role and requirements
- Refines recommendations when requirements change
- Compares assessments when asked
- Refuses off-topic questions

## Tech Stack
- FastAPI — REST API
- LangChain + Groq (LLaMA 3.1) — LLM
- ChromaDB + Sentence Transformers — Vector search
- SHL Product Catalog — 377 Individual Test Solutions

## API Endpoints
- `GET /health` — Health check
- `POST /chat` — Conversational recommendation

## Setup
```bash
pip install -r requirements.txt
python scripts/build_vectorstore.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Example
```json
POST /chat
{
  "messages": [
    {"role": "user", "content": "I am hiring a Java developer"}
  ]
}
```