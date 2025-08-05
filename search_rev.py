from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
import os
from sqlalchemy.sql import cast
from bs4 import BeautifulSoup


# from sqlalchemy.dialects.postgresql import VECTOR  # import pgvector dialect


# Step 1: Setup
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
engine = create_engine("postgresql://mukhtada:password@localhost:5432/chatbot")
model = SentenceTransformer("intfloat/multilingual-e5-small", device="cpu")


def get_embedding(text: str) -> str:
    """Convert query into pgvector-compatible string"""
    vec = model.encode(text, normalize_embeddings=True).tolist()
    return "[" + ",".join(map(str, vec)) + "]"


def extract_text_from_html(html_content: str) -> str:
    """Extracts and cleans text from <body> tag of HTML"""
    soup = BeautifulSoup(html_content or "", "html.parser")
    body = soup.body
    if body:
        return body.get_text(separator=" ", strip=True)
    return soup.get_text(separator=" ", strip=True)


def semantic_search(query: str, top_k: int = 5):
    """Fast semantic search using ivfflat index on embedding_vector"""
    vec = get_embedding(query)

    # Safe since `vec` is generated internally
    vector_literal = (
        vec  # already in PostgreSQL-compatible format, e.g., [0.1, 0.2, ...]
    )

    sql = f"""
        SET enable_seqscan = OFF;

        SELECT title, LEFT(content, 500) AS preview, url,
               1 - (embedding_vector <#> '{vector_literal}'::vector) AS similarity
        FROM pages_fix
        WHERE embedding_vector IS NOT NULL
        ORDER BY embedding_vector <#> '{vector_literal}'::vector
        LIMIT {top_k};
    """

    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()

    return rows


def build_prompt_with_context(query: str, rows):
    context_parts = []
    for i, row in enumerate(rows):
        title = row.title or "(no title)"
        raw_html = row.preview or ""
        plain_text = extract_text_from_html(raw_html)
        context_parts.append(f"[{i+1}] {title}:\n{plain_text}...\n")

    context = "\n---\n".join(context_parts)

    prompt = f"""
You are an assistant. Use the context below to answer the question.

Context:
{context}

Question:
{query}

Answer:"""

    return prompt.strip()


def simulate_rag(query: str, top_k: int = 5):
    """Run full RAG simulation from query input"""
    rows = semantic_search(query, top_k=top_k)
    prompt = build_prompt_with_context(query, rows)

    print("\n===== 🔍 RAG Simulation Prompt =====\n")
    print(prompt)
    print("\n====================================\n")


# Example run
if __name__ == "__main__":
    q = input("📝 Masukkan pertanyaan: ").strip()
    simulate_rag(q, top_k=5)
