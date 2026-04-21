import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.ingestion import convert_to_markdown
from app.ai import generate_onboarding_steps
from app.database import get_db, OnboardingStep

router = APIRouter(tags=["Onboarding"])

@router.get("/onboarding/project/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    steps = (
        db.query(OnboardingStep)
        .filter(OnboardingStep.project_id == project_id)
        .order_by(OnboardingStep.step_order)
        .all()
    )

    if not steps:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado"
        )

    return {
        "project_id": project_id,
        "total_steps": len(steps),
        "files": list(set([s.filename for s in steps])),
        "steps": [
            {
                "order": s.step_order,
                "title": s.title,
                "content": s.content,
                "filename": s.filename
            }
            for s in steps
        ]
    }

@router.post("/onboarding/project/ingest")
async def ingest_document(
    project_id: str | None = None,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    if not project_id:
        project_id = str(uuid.uuid4())

    all_steps = []

    for file in files:
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ("pdf", "docx"):
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado: {file.filename}. Envie PDF ou DOCX."
            )

        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo vazio: {file.filename}"
            )

        markdown = convert_to_markdown(contents, file.filename)
        if not markdown:
            raise HTTPException(
                status_code=422,
                detail=f"Não foi possível extrair texto do arquivo: {file.filename}"
            )

        steps = generate_onboarding_steps(markdown)

        db.query(OnboardingStep).filter_by(
            project_id=project_id,
            filename=file.filename
        ).delete()

        for i, step in enumerate(steps):
            db.add(OnboardingStep(
                project_id=project_id,
                filename=file.filename,
                step_order=i + 1,
                title=step["title"],
                content=step["content"],
            ))

        all_steps.append({
            "filename": file.filename,
            "steps": steps
        })

    db.commit()

    return {
        "project_id": project_id,
        "total_files": len(files),
        "files": all_steps
    }