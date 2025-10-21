import openai
from fastapi import Request
from sqlmodel import Session
from app.database.config import engine


def get_openai_client(request: Request) -> openai.OpenAI:
    return request.app.state.openai_client

def get_session():
    with Session(engine) as session:
        yield session