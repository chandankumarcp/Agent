"""
File readers for research papers and source code.
Supports PDF, DOCX, Markdown, plain text, Jupyter notebooks, and common code formats.
"""

import json
import re
from pathlib import Path


# --------------------------------------------------------------------------- #
# Folder scanner
# --------------------------------------------------------------------------- #

def scan_folder(
    folder: Path,
    paper_extensions: set[str],
    code_extensions: set[str],
) -> tuple[list[Path], list[Path]]:
    """Return sorted lists of (paper files, code files) found under `folder`."""
    paper_files: list[Path] = []
    code_files: list[Path] = []

    skip_dirs = {".git", "__pycache__", ".venv", "venv", "env", "node_modules", ".tox", "dist", "build"}

    for path in sorted(folder.rglob("*")):
        if path.is_dir():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        suffix = path.suffix.lower()
        if suffix in paper_extensions:
            paper_files.append(path)
        elif suffix in code_extensions:
            code_files.append(path)

    return paper_files, code_files


# --------------------------------------------------------------------------- #
# Paper readers
# --------------------------------------------------------------------------- #

def read_paper(path: Path) -> str:
    """Dispatch to the appropriate reader based on file extension."""
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            return _read_pdf(path)
        if suffix == ".docx":
            return _read_docx(path)
        if suffix in {".md", ".txt", ".rst"}:
            return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return f"[Error reading {path.name}: {exc}]"
    return ""


def _read_pdf(path: Path) -> str:
    """Extract text from a PDF using pdfplumber (preferred) or PyPDF2 as fallback."""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)
    except ImportError:
        pass

    try:
        import PyPDF2
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join(
                (reader.pages[i].extract_text() or "") for i in range(len(reader.pages))
            )
    except ImportError:
        return "[PDF reading unavailable: install pdfplumber or PyPDF2]"


def _read_docx(path: Path) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join(para.text for para in doc.paragraphs)
    except ImportError:
        return "[DOCX reading unavailable: install python-docx]"


# --------------------------------------------------------------------------- #
# Code readers
# --------------------------------------------------------------------------- #

def read_code_file(path: Path) -> str:
    """Read source code; handle Jupyter notebooks specially."""
    suffix = path.suffix.lower()
    try:
        if suffix == ".ipynb":
            return _read_notebook(path)
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return f"[Error reading {path.name}: {exc}]"


def _read_notebook(path: Path) -> str:
    """Extract code and markdown cells from a Jupyter notebook."""
    with open(path, encoding="utf-8", errors="ignore") as f:
        nb = json.load(f)

    chunks: list[str] = []
    for cell in nb.get("cells", []):
        cell_type = cell.get("cell_type", "")
        source = "".join(cell.get("source", []))
        if not source.strip():
            continue
        if cell_type == "code":
            chunks.append(f"```python\n{source}\n```")
        elif cell_type == "markdown":
            chunks.append(source)

    return "\n\n".join(chunks)
