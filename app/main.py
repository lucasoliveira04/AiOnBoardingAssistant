from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import onboarding

app = FastAPI(
    title="AI Project Onboarding Assistant",
    description="Assistente inteligente para onboarding de desenvolvedores",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(onboarding.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Project Onboarding Assistant rodando!"}