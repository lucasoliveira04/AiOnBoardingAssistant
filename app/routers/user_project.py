from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import OnboardingStep, User, UserProject, get_db

router = APIRouter()


# Associar usuário a projeto
@router.post("/users/{user_id}/projects/{project_id}")
def associate_user_project(
    user_id: str,
    project_id: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    relation = UserProject(
        user_id=user_id,
        project_id=project_id
    )

    db.add(relation)
    db.commit()

    return {
        "user_id": user_id,
        "project_id": project_id,
        "message": "User associado ao projeto"
    }


@router.get("/users/{user_id}/projects")
def get_user_projects(
    user_id: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    projects = (
        db.query(
            UserProject.project_id,
            OnboardingStep.project_name
        )
        .join(OnboardingStep, OnboardingStep.project_id == UserProject.project_id)
        .filter(UserProject.user_id == user_id)
        .distinct()
        .all()
    )

    result = []

    for project in projects:

        steps = (
            db.query(OnboardingStep)
            .filter(OnboardingStep.project_id == project.project_id)
            .order_by(OnboardingStep.step_order)
            .all()
        )

        result.append({
            "project_id": project.project_id,
            "project_name": project.project_name,
            "steps": {
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
        })

    return {
        "user": {
            "id": user.id,
            "nome": user.nome,
            "sobrenome": user.sobrenome,
            "cargo": user.cargo
        },
        "projects": result
    }


@router.get("/projects/{project_id}/users")
def get_project_users(
    project_id: str,
    db: Session = Depends(get_db)
):
    results = (
        db.query(User, UserProject)
        .join(UserProject, User.id == UserProject.user_id)
        .filter(UserProject.project_id == project_id)
        .all()
    )

    return {
        "project_id": project_id,
        "users": [
            {
                "id": user.id,
                "nome": user.nome,
                "sobrenome": user.sobrenome,
                "cargo": user.cargo,
                "associated_at": relation.created_at
            }
            for user, relation in results
        ]
    }


@router.delete("/users/{user_id}/projects/{project_id}")
def remove_user_from_project(
    user_id: str,
    project_id: str,
    db: Session = Depends(get_db)
):
    relation = (
        db.query(UserProject)
        .join(User, User.id == UserProject.user_id)
        .filter(
            UserProject.user_id == user_id,
            UserProject.project_id == project_id
        )
        .first()
    )

    if not relation:
        raise HTTPException(
            status_code=404,
            detail="Relação não encontrada"
        )

    db.delete(relation)
    db.commit()

    return {
        "message": "Usuário removido do projeto",
        "user_id": user_id,
        "project_id": project_id
    }