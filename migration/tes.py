from sqlalchemy import create_engine, text

# Connect to PostgreSQL
engine = create_engine("postgresql://mukhtada:password@localhost:5432/chatbot")


def migrate_embeddings():
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
            SELECT id, embedding
            FROM pages
            WHERE embedding_vector IS NULL AND embedding IS NOT NULL
        """
            )
        ).fetchall()

        print(f"Found {len(rows)} rows to migrate.")

        for row in rows:
            page_id = row.id
            embedding_data = row.embedding

            try:
                # Decode JSON if needed
                if isinstance(embedding_data, str):
                    import json

                    vector = json.loads(embedding_data)
                elif isinstance(embedding_data, list):
                    vector = embedding_data
                else:
                    raise ValueError("Unsupported embedding type")

                if not all(isinstance(x, (int, float)) for x in vector):
                    raise ValueError("Embedding must be a list of numbers")

                vector_str = "[" + ",".join(map(str, vector)) + "]"

                # Use %(param)s syntax
                conn.execute(
                    text(
                        """
                    UPDATE pages
                    SET embedding_vector = %(vec)s::vector
                    WHERE id = %(id)s
                """
                    ),
                    {"vec": vector_str, "id": page_id},
                )

            except Exception as e:
                print(f"❌ Error processing ID {page_id}: {e}")

        print("✅ Embedding migration complete.")


if __name__ == "__main__":
    migrate_embeddings()
