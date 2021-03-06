import typing
from fastapi import Depends, FastAPI, HTTPException, Request, Form
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="polls/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/questions/", response_model=schemas.Question)
def create_question(question_schema: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db=db, question_schema=question_schema)


@app.get("/questions/", response_model=typing.List[schemas.Question], response_class=HTMLResponse)
def read_questions(request: Request, limit: int = 5, db: Session = Depends(get_db)):
    questions = crud.get_questions(db, limit=limit)
    return templates.TemplateResponse("questions.html", {'request': request, 'questions': questions})


@app.post("/questions/{question_id}/choice/", response_model=schemas.Choice)
def create_choice(question_id: int, choice: schemas.ChoiceCreate, db: Session = Depends(get_db)):
    return crud.create_choice(db=db, choice=choice, question_id=question_id)


@app.get("/questions/{question_id}", response_model=typing.List[schemas.Choice], response_class=HTMLResponse)
def read_choices(request: Request, question_id: int, db: Session = Depends(get_db)):
    choices = crud.get_choices(db, question_id=question_id)
    return templates.TemplateResponse("choices.html", {
        'request': request, 'choices': choices, 'question_id': question_id
    })


@app.post("/questions/{question_id}/vote/")
def make_vote(question_id: int, vote: schemas.Vote, db: Session = Depends(get_db)):
    return crud.make_vote(db=db, question_id=question_id, vote=vote)


@app.post("/questions/{question_id}/answer/")
def make_answer(request: Request, question_id: int, choice: int = Form(), db: Session = Depends(get_db)):
    crud.make_answer(db=db, question_id=question_id, choice=choice)
    choices = crud.get_voting_results(db, question_id)
    return templates.TemplateResponse("results.html", {
        'request': request, 'question_id': question_id, 'choices': choices
    })
