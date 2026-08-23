import re


def generate_answer(
    question: str,
    evidence_result: dict
) -> dict:
    """
    Generate a grounded answer using retrieved evidence.

    Filters raw document chunks into concise matching lines locally 
    without needing external API keys. Refuses if evidence is missing.
    """

    status = evidence_result.get("status", "not_found")
    evidence = evidence_result.get("evidence", [])

    # Never answer when there is no supporting evidence.
    if status != "verified" or not evidence:
        return {
            "status": "not_found",
            "answer": (
                "I couldn't find this information "
                "in the provided documents."
            ),
            "sources": []
        }

    # Use the strongest evidence first.
    best_evidence = sorted(
        evidence,
        key=lambda item: item.get("score", 0.0),
        reverse=True
    )

    primary = best_evidence[0]
    raw_text = primary.get("text", "").strip()

    # Common search filler words to exclude
    stop_words = {
        "what", "is", "the", "a", "an", "who", "where", 
        "how", "for", "of", "in", "to", "does", "give", "me"
    }

    # Extract clean keywords from the query
    keywords = [
        word.lower() 
        for word in re.findall(r"\b\w+\b", question) 
        if word.lower() not in stop_words
    ]

    # Split raw text into distinct sentences or lines
    lines = [
        line.strip() 
        for line in re.split(r"[\n\.]", raw_text) 
        if line.strip()
    ]

    # Filter lines that match query keywords
    matching_lines = []
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in keywords):
            matching_lines.append(line)

    # Format answer: join top matching lines or fallback to full raw text
    if matching_lines:
        unique_lines = list(dict.fromkeys(matching_lines))
        answer = " ".join(unique_lines[:3])
    else:
        answer = raw_text

    source = {
        "document": primary.get("document"),
        "page": primary.get("page"),
        "section": primary.get("section"),
        "score": primary.get("score"),
    }

    return {
        "status": status,
        "answer": answer,
        "sources": [source]
    }