from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ingestion import convert_to_markdown, split_into_chunks

router = APIRouter(tags=["Onboarding"])


@router.post("/ask")
def ask_question():
    return {"answer": "resposta de exemplo"}


@router.get("/projects")
def list_projects():
    return {
        "projects": [
            {"id": "default", "name": "Projeto Demo", "status": "indexed", "files": 42},
        ]
    }


@router.get("/projects/{project_id}/summary")
def get_project_summary(project_id: str):
    return {
        "project_id": project_id,
        "name": "Projeto Demo",
        "main_modules": ["auth", "users", "products", "orders"],
    }


@router.post("/onboarding/project/{project_id}/ingest")
async def ingest_document(project_id: str, file: UploadFile = File(...)):
    allowed = ("pdf", "docx")
    ext = file.filename.rsplit(".", 1)[-1].lower()

    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Formato não suportado. Envie um PDF ou DOCX.")

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    markdown = convert_to_markdown(contents, file.filename)

    if not markdown:
        raise HTTPException(status_code=422, detail="Não foi possível extrair texto do arquivo.")

    chunks = split_into_chunks(markdown)

    return {
        "project_id": project_id,
        "filename": file.filename,
        "format": ext,
        "total_chars": len(markdown),
        "total_chunks": len(chunks),
        "chunks": chunks,
    }