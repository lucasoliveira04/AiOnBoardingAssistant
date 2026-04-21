from pypdf import PdfReader
from typing import List
import io

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()


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