import tiktoken


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count the number of tokens in a string using OpenAI's tiktoken.

    Parameters:
        text (str): The input text.
        model (str): The model to match tokenization. Default: gpt-3.5-turbo

    Returns:
        int: Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # fallback

    tokens = encoding.encode(text)
    return len(tokens)
