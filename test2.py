from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
import requests

app = FastAPI()

# Database setup
DATABASE_URL = "postgresql://myuser:mypassword@postgres/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)
    answer_text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic model for request
class QuizRequest(BaseModel):
    questions_num: int

# Pydantic model for response
class QuizResponse(BaseModel):
    id: int
    question_text: str
    answer_text: str
    created_at: datetime

@app.post("/quiz")
def generate_quiz(quiz_request: QuizRequest):
    db = SessionLocal()
    try:
        # Get questions from the public API
        response = requests.get(f"https://jservice.io/api/random?count={quiz_request.questions_num}")
        response.raise_for_status()
        questions_data = response.json()

        # Save unique questions to the database
        for data in questions_data:
            question = db.query(QuizQuestion).filter_by(question_text=data["question"]).first()
            if not question:
                new_question = QuizQuestion(**data)
                db.add(new_question)
                db.commit()
                db.refresh(new_question)

        # Get a question from the database
        question = db.query(QuizQuestion).first()

        if question:
            return question
        else:
            raise HTTPException(status_code=404, detail="No questions available")

    finally:
        db.close()
