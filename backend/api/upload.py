import os
import re
import traceback

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
)

from backend.api.deps import get_pipeline
from backend.rag.pipeline import KnowledgePipeline
from backend.rag.ingest import SUPPORTED_EXTENSIONS


router = APIRouter()

UPLOAD_DIR = os.path.join(
    "backend",
    "data",
    "uploads",
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    pipeline: KnowledgePipeline = Depends(
        get_pipeline
    ),
):
    """
    Upload and index multiple documents.

    Supported formats:
        PDF
        DOCX
        TXT
        Markdown
        HTML
    """

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one document.",
        )

    saved_paths = []
    uploaded_names = []

    try:

        # --------------------------------------------------
        # 1. Validate all files first
        # --------------------------------------------------

        for file in files:

            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="A file was uploaded without a filename.",
                )

            extension = os.path.splitext(
                file.filename
            )[1].lower()

            if extension not in SUPPORTED_EXTENSIONS:
                supported = ", ".join(
                    sorted(
                        SUPPORTED_EXTENSIONS
                    )
                )

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Unsupported file type: {extension}. "
                        f"Supported formats: {supported}"
                    ),
                )

        # --------------------------------------------------
        # 2. Save all files
        # --------------------------------------------------

        for file in files:

            safe_filename = re.sub(
                r"[^a-zA-Z0-9_.-]",
                "_",
                file.filename,
            )

            file_path = os.path.join(
                UPLOAD_DIR,
                safe_filename,
            )

            content = await file.read()

            with open(
                file_path,
                "wb",
            ) as buffer:
                buffer.write(content)

            saved_paths.append(
                file_path
            )

            uploaded_names.append(
                file.filename
            )

        # --------------------------------------------------
        # 3. Add ALL documents to the shared pipeline
        # --------------------------------------------------

        stats = pipeline.load_documents(
            saved_paths
        )

        return {
            "message": (
                f"Successfully processed "
                f"{len(uploaded_names)} document(s)."
            ),
            "files": uploaded_names,
            "stats": stats,
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            "\n--- DETAILED UPLOAD ERROR ---"
        )

        traceback.print_exc()

        print(
            "-----------------------------\n"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )