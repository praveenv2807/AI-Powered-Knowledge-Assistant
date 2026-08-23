import re


def estimate_tokens(text: str) -> int:
    """
    Simple token estimate for chunk sizing.

    This is an approximation, not a tokenizer.
    """
    return max(1, len(text.split()))


def split_text(text: str, max_words: int = 500, overlap_words: int = 75) -> list[str]:
    """
    Split text into overlapping chunks.

    max_words:
        Approximate maximum words per chunk.

    overlap_words:
        Number of words repeated between adjacent chunks.
    """

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + max_words, len(words))

        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap_words

    return chunks


def create_chunks(pages: list[dict]) -> list[dict]:
    """
    Convert page-level extracted text into searchable chunks.

    Each chunk preserves:
    - document
    - page
    - section
    - chunk_id
    - text
    """

    chunks = []
    chunk_counter = 1

    for page in pages:
        text = page.get("text", "").strip()

        if not text:
            continue

        # For the first version, use the first meaningful line
        # as a simple section hint.
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        section = lines[0] if lines else "Unknown"

        page_chunks = split_text(
            text,
            max_words=500,
            overlap_words=75
        )

        for chunk_text in page_chunks:
            chunks.append(
                {
                    "chunk_id": f"chunk_{chunk_counter}",
                    "document": page["document"],
                    "page": page["page"],
                    "section": section,
                    "text": chunk_text,
                    "token_estimate": estimate_tokens(chunk_text),
                }
            )

            chunk_counter += 1

    return chunks