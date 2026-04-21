from pydantic import BaseModel

from app.ProjectEnum import ProjectName

class CreateProjectRequest(BaseModel):
    project_name: ProjectName