from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.ingestion import convert_to_markdown
from app.ai import generate_onboarding_steps
from app.database import get_db, OnboardingStep

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


@router.get("/onboarding/project/{project_id}/steps")
def get_onboarding_steps(project_id: str, db: Session = Depends(get_db)):
    steps = (
        db.query(OnboardingStep)
        .filter_by(project_id=project_id)
        .order_by(OnboardingStep.step_order)
        .all()
    )
    return {
        "project_id": project_id,
        "steps": [
            {"order": s.step_order, "title": s.title, "content": s.content}
            for s in steps
        ],
    }


@router.post("/onboarding/project/{project_id}/ingest")
async def ingest_document(project_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Formato não suportado. Envie um PDF ou DOCX.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    markdown = convert_to_markdown(contents, file.filename)
    if not markdown:
        raise HTTPException(status_code=422, detail="Não foi possível extrair texto do arquivo.")

    steps = generate_onboarding_steps(markdown)

    db.query(OnboardingStep).filter_by(project_id=project_id, filename=file.filename).delete()
    for i, step in enumerate(steps):
        db.add(OnboardingStep(
            project_id=project_id,
            filename=file.filename,
            step_order=i + 1,
            title=step["title"],
            content=step["content"],
        ))
    db.commit()

    return {
        "project_id": project_id,
        "filename": file.filename,
        "total_steps": len(steps),
        "steps": steps,
    }