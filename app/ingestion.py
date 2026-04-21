from pypdf import PdfReader
from docx import Document
from typing import List
import io
import re

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


def pdf_to_markdown(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    sections = []

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        lines = text.splitlines()
        md_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            is_short = len(line) < 60
            is_title_case = line.istitle() or line.isupper()
            ends_without_punct = not line[-1] in ".,:;?!)\"'"

            if is_short and is_title_case and ends_without_punct:
                md_lines.append(f"\n## {line}\n")
            else:
                md_lines.append(line)

        sections.append(f"<!-- page {i} -->\n" + "\n".join(md_lines))

    return "\n\n".join(sections).strip()


def docx_to_markdown(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    md_lines = []

    HEADING_MAP = {
        "Heading 1": "#",
        "Heading 2": "##",
        "Heading 3": "###",
        "Heading 4": "####",
    }

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style = para.style.name
        prefix = HEADING_MAP.get(style)

        if prefix:
            md_lines.append(f"\n{prefix} {text}\n")
        else:
            md_lines.append(text)

    return "\n".join(md_lines).strip()


def convert_to_markdown(file_bytes: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        return pdf_to_markdown(file_bytes)
    elif ext == "docx":
        return docx_to_markdown(file_bytes)
    else:
        raise ValueError(f"Formato não suportado: .{ext}")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            breakpoint = text.rfind("\n", start, end)
            if breakpoint == -1:
                breakpoint = text.rfind(" ", start, end)
            if breakpoint != -1:
                end = breakpoint

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks