from sentence_transformers import SentenceTransformer
from typing import List
import torch

# Cache model to avoid reloading
_loaded_models = {}


def get_embedding(
    content: str, model: str = "intfloat/multilingual-e5-small"
) -> List[float]:
    """
    Convert a given content string into a vector embedding using SentenceTransformer.

    Parameters:
        content (str): The text content to be embedded.
        model (str): The HuggingFace model name. Default is multilingual-e5-small.

    Returns:
        List[float]: The embedding vector as a list of floats.
    """

    # Load model only once (reuse)
    if model not in _loaded_models:
        _loaded_models[model] = SentenceTransformer(model)

    transformer = _loaded_models[model]

    # For e5 models, prepend "passage: " for document content
    if "e5" in model:
        content = f"passage: {content.strip()}"

    # Normalize (important for cosine similarity)
    embedding = transformer.encode(content, normalize_embeddings=True)

    # Convert to list for storage (e.g., JSON/DB)
    return embedding.tolist()
