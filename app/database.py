from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class OnboardingStep(Base):
    __tablename__ = "onboarding_steps"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    project_id  = Column(String, nullable=False, index=True)
    project_name = Column(String, nullable=False)
    filename    = Column(String, nullable=False)
    step_order  = Column(Integer, nullable=False)
    title       = Column(String, nullable=False)
    content     = Column(Text, nullable=False)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)