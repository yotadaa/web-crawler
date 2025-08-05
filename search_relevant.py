import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from migration.page import Page
from sentence_transformers import SentenceTransformer
import os
import logging
import sys
import contextlib

os.environ["TF_CPP_MIN_LOG_LEVEL"] = (
    "3"  # 0 = all logs, 1 = filter INFO, 2 = +WARNING, 3 = only ERROR
)
logging.getLogger("tensorflow").setLevel(logging.ERROR)


@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


_loaded_models = {}


def get_embedding(text: str, model: str = "intfloat/multilingual-e5-small"):
    if model not in _loaded_models:
        # Paksa pakai CPU
        _loaded_models[model] = SentenceTransformer(model, device="cpu")
    return _loaded_models[model].encode(text, normalize_embeddings=True).tolist()


# Setup koneksi
engine = create_engine("postgresql://mukhtada:password@localhost:5432/chatbot")
Session = sessionmaker(bind=engine)
session = Session()


# Fungsi cosine similarity
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# Fungsi cari halaman relevan
def search_relevant_pages(
    keyword: str, top_k: int = 5, model_name="intfloat/multilingual-e5-small"
):
    print(f"🔍 Searching for: {keyword}")
    query_embedding = get_embedding(keyword.lower(), model=model_name)

    results = []
    for page in session.query(Page).filter(Page.embedding != None).all():
        similarity = cosine_similarity(query_embedding, page.embedding)
        results.append((similarity, page))

    # Urutkan berdasarkan similarity tertinggi
    results.sort(key=lambda x: x[0], reverse=True)

    # Tampilkan hasil
    print(f"\n📄 Top {top_k} results:\n")
    for sim, page in results[:top_k]:
        # print(f"[{sim:.4f}] {page.url}")
        print(f"Title: {page.title or '(no title)'}")
        print(f"Preview: {page.content[:200]}...\n")


# Contoh pemakaian
if __name__ == "__main__":
    q = input("Input Keyword: ").strip()
    search_relevant_pages(q, top_k=5)
