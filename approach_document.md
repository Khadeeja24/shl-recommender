---
title: SHL Assessment Recommender — Approach Document
---

# SHL Assessment Recommender — Approach Document

**Candidate:** Khadeeja
**Role:** AI Intern — SHL Labs
**Deployment:** https://khadeejaf-shl-recommender.hf.space

---

## 1. Problem Decomposition

Hiring managers often cannot articulate assessment needs precisely upfront.
The core challenge is bridging vague hiring intent ("I need an assessment")
to a grounded shortlist of SHL Individual Test Solutions through dialogue.

Four sub-problems were identified:
- **Retrieval** — finding relevant assessments from 377 catalog items
- **Dialogue management** — knowing when to clarify vs recommend vs compare
- **Schema compliance** — strict JSON output for automated evaluation
- **Scope enforcement** — refusing off-topic queries reliably

---

## 2. Retrieval Design

A **hybrid BM25 + TF-IDF** approach was chosen over vector search:

**BM25Okapi** handles exact keyword matching — critical for SHL-specific
test names like "OPQ32r", "Java 8 (New)", "Verify G+". These names are
not semantically similar to anything — they must be matched exactly.

**TF-IDF with bigrams** handles semantic similarity across descriptions,
job levels, and categories — useful for role-based queries like
"customer service agent" or "senior data scientist".

Both scores are normalized to [0,1] and combined 50/50:

final_score = 0.5 * bm25_score + 0.5 * tfidf_score

Top 15 candidates are retrieved per query and injected into the
LLM context window as dynamic catalog context.

**Why not ChromaDB + sentence-transformers?**
Tested initially but exceeded 512MB RAM on free hosting. BM25 + TF-IDF
uses ~50MB, has zero cold start delay, and performs better for
keyword-heavy catalog search.

---

## 3. Agent Design

**LLM:** Groq LLaMA 3.3 70B Versatile with native JSON output mode

**4 conversational behaviors implemented:**

| Behavior | Trigger | Action |
|---|---|---|
| Clarify | Vague query, missing context | Ask ONE focused question |
| Recommend | Role + seniority + skills known | Return 1-10 assessments |
| Refine | User changes requirements | Update shortlist, don't restart |
| Compare | "Difference between X and Y?" | Answer from catalog data only |

**Guardrails:**
- URL validation — only `shl.com` URLs pass through to response
- JSON mode enforced via Groq `response_format` parameter
- Off-topic refusal with examples in system prompt
- Max 10 recommendations enforced in code
- Never recommends on turn 1 for vague queries

---

## 4. Context Engineering

System prompt contains:
- Role definition and 4 behavior descriptions
- 6 few-shot examples covering all behaviors including edge cases
- Dynamic catalog context (top 15 retrieved items per query)
- Strict output schema with field-level instructions
- Explicit refusal examples for off-topic queries

Query for retrieval combines last 3 user messages for
context-aware search that improves with conversation history.

---

## 5. What Didn't Work

| Attempt | Problem | Fix |
|---|---|---|
| ChromaDB + sentence-transformers | 512MB RAM exceeded | Switched to BM25 + TF-IDF |
| LLaMA 3.1 8B | Inconsistent JSON | Upgraded to LLaMA 3.3 70B + JSON mode |
| BeautifulSoup scraping | CloudFront 403 block | Used official SHL catalog JSON |
| Render deployment | 512MB RAM limit | Moved to HuggingFace Spaces Docker |

---

## 6. Evaluation

Tested against all 10 public conversation traces manually:

- Schema compliance: 100% on all turns
- Vague query handling: Correctly withholds recommendations on turn 1
- Refinement: Updates shortlist without restarting
- Off-topic refusal: Correctly refuses salary, legal, HR questions
- Comparison: Answers from catalog data, not model priors
- URL validity: All URLs verified against official SHL catalog

---

## 7. Stack Summary

| Component | Technology |
|---|---|
| LLM | Groq LLaMA 3.3 70B Versatile |
| Retrieval | BM25Okapi + TF-IDF (rank-bm25, scikit-learn) |
| API | FastAPI + Uvicorn |
| Deployment | HuggingFace Spaces (Docker) |
| Catalog | Official SHL JSON — 377 Individual Test Solutions |
| UI | Vanilla HTML/CSS/JS served by FastAPI |

## 8. AI Tools Used

Claude (Anthropic) was used for code assistance, debugging deployment
issues, and iterating on prompt design. All design decisions and
trade-offs were made and understood by the candidate.