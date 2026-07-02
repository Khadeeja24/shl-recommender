import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

CATALOG_PATH = "data/catalog.json"

def load_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

catalog = load_catalog()

def build_doc(item):
    name = str(item.get("name", ""))
    description = str(item.get("description", ""))
    keys = str(item.get("keys", ""))
    job_levels = item.get("job_levels", [])
    if isinstance(job_levels, list):
        job_levels = ", ".join(job_levels)
    duration = str(item.get("duration", ""))
    return f"{name} {name} {keys} {description} {job_levels} {duration}"

# Build both indexes
documents = [build_doc(item) for item in catalog]

# TF-IDF
tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1,2))
tfidf_matrix = tfidf.fit_transform(documents)

# BM25
tokenized = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized)

def search(query: str, n_results: int = 15):
    try:
        # BM25 scores
        bm25_scores = np.array(bm25.get_scores(query.lower().split()))

        # TF-IDF scores
        query_vec = tfidf.transform([query])
        tfidf_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

        # Normalize both to 0-1
        if bm25_scores.max() > 0:
            bm25_scores = bm25_scores / bm25_scores.max()
        if tfidf_scores.max() > 0:
            tfidf_scores = tfidf_scores / tfidf_scores.max()

        # Combine: 50% BM25 + 50% TF-IDF
        combined = 0.5 * bm25_scores + 0.5 * tfidf_scores
        top_indices = np.argsort(combined)[::-1][:n_results]

        results = []
        for i in top_indices:
            if combined[i] > 0:
                item = catalog[i]
                job_levels = item.get("job_levels", [])
                if isinstance(job_levels, list):
                    job_levels = ", ".join(job_levels)
                results.append({
                    "name": str(item.get("name", "")),
                    "url": str(item.get("link", "")),
                    "keys": str(item.get("keys", "")),
                    "description": str(item.get("description", "")),
                    "duration": str(item.get("duration", "")),
                    "job_levels": job_levels
                })
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []