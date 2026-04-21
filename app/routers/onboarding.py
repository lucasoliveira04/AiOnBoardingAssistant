from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ingestion import extract_text_from_pdf, split_into_chunks

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
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são suportados.")

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    text = extract_text_from_pdf(contents)

    if not text:
        raise HTTPException(status_code=422, detail="Não foi possível extrair texto do PDF.")

    chunks = split_into_chunks(text)

    return {
        "project_id": project_id,
        "filename": file.filename,
        "total_chars": len(text),
        "total_chunks": len(chunks),
        "chunks": chunks,
    }