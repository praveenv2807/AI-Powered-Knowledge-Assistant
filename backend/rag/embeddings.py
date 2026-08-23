from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_embedding_model():
    """
    Load the embedding model once and reuse it.
    """

    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def generate_embeddings(texts: list[str]):
    """
    Convert a list of text strings into embedding vectors.
    """

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings