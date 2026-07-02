import json
import os
import re
from groq import Groq
from app.retriever import search
from app.prompts import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def format_catalog_context(items):
    lines = []
    for item in items:
        line = (
            f"- Name: {item['name']} | "
            f"Category: {item['keys']} | "
            f"Duration: {item['duration']} | "
            f"Job Levels: {item['job_levels']} | "
            f"URL: {item['url']}"
        )
        lines.append(line)
    return "\n".join(lines)

def extract_search_query(messages):
    # Use last 3 user messages for context-aware search
    user_messages = [m["content"] for m in messages if m["role"] == "user"]
    return " ".join(user_messages[-3:])

def parse_json_response(content: str) -> dict:
    # Try direct parse
    try:
        return json.loads(content)
    except:
        pass
    # Try extracting JSON block
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    # Fallback
    return {
        "reply": content.strip(),
        "recommendations": [],
        "end_of_conversation": False
    }

def chat(messages: list) -> dict:
    # Context-aware search using conversation history
    query = extract_search_query(messages)
    catalog_items = search(query, n_results=15)
    catalog_context = format_catalog_context(catalog_items)

    system_prompt = SYSTEM_PROMPT.format(catalog_context=catalog_context)

    groq_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # much smarter model
        messages=groq_messages,
        temperature=0.1,
        max_tokens=2000,
        response_format={"type": "json_object"}  # force JSON output
    )

    content = response.choices[0].message.content
    result = parse_json_response(content)

    # Validate and clean recommendations
    recommendations = result.get("recommendations", [])
    if not isinstance(recommendations, list):
        recommendations = []

    valid_recs = []
    for rec in recommendations[:10]:
        if isinstance(rec, dict) and rec.get("name") and rec.get("url"):
            # Only allow real SHL URLs
            url = str(rec.get("url", ""))
            if "shl.com" in url:
                valid_recs.append({
                    "name": str(rec.get("name", "")),
                    "url": url,
                    "test_type": str(rec.get("test_type", ""))
                })

    return {
        "reply": str(result.get("reply", "")),
        "recommendations": valid_recs,
        "end_of_conversation": bool(result.get("end_of_conversation", False))
    }import json
import os
import re
from groq import Groq
from app.retriever import search
from app.prompts import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def format_catalog_context(items):
    lines = []
    for item in items:
        line = (
            f"- Name: {item['name']} | "
            f"Category: {item['keys']} | "
            f"Duration: {item['duration']} | "
            f"Job Levels: {item['job_levels']} | "
            f"URL: {item['url']}"
        )
        lines.append(line)
    return "\n".join(lines)

def extract_search_query(messages):
    # Use last 3 user messages for context-aware search
    user_messages = [m["content"] for m in messages if m["role"] == "user"]
    return " ".join(user_messages[-3:])

def parse_json_response(content: str) -> dict:
    # Try direct parse
    try:
        return json.loads(content)
    except:
        pass
    # Try extracting JSON block
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    # Fallback
    return {
        "reply": content.strip(),
        "recommendations": [],
        "end_of_conversation": False
    }

def chat(messages: list) -> dict:
    # Context-aware search using conversation history
    query = extract_search_query(messages)
    catalog_items = search(query, n_results=15)
    catalog_context = format_catalog_context(catalog_items)

    system_prompt = SYSTEM_PROMPT.format(catalog_context=catalog_context)

    groq_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # much smarter model
        messages=groq_messages,
        temperature=0.1,
        max_tokens=2000,
        response_format={"type": "json_object"}  # force JSON output
    )

    content = response.choices[0].message.content
    result = parse_json_response(content)

    # Validate and clean recommendations
    recommendations = result.get("recommendations", [])
    if not isinstance(recommendations, list):
        recommendations = []

    valid_recs = []
    for rec in recommendations[:10]:
        if isinstance(rec, dict) and rec.get("name") and rec.get("url"):
            # Only allow real SHL URLs
            url = str(rec.get("url", ""))
            if "shl.com" in url:
                valid_recs.append({
                    "name": str(rec.get("name", "")),
                    "url": url,
                    "test_type": str(rec.get("test_type", ""))
                })

    return {
        "reply": str(result.get("reply", "")),
        "recommendations": valid_recs,
        "end_of_conversation": bool(result.get("end_of_conversation", False))
    }