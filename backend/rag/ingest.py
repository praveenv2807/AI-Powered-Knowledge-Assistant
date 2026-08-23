from pathlib import Path
import pymupdf


def extract_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF page by page.

    Returns a list containing:
    - document name
    - page number
    - extracted text
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported right now.")

    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()

        if text:
            pages.append(
                {
                    "document": path.name,
                    "page": page_number,
                    "text": text,
                }
            )

    document.close()

    return pages