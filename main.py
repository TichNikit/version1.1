import uvicorn
# uvicorn main:app --reload
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head
from fastapi import FastAPI, status, Body, HTTPException, Request
from fastapi.responses import HTMLResponse

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db

from typing import Annotated
from fastapi.templating import Jinja2Templates

from app.models.game import Game
from app.models.user import User
from app.models.user_game_feedback import UserGameFeedback
from app.models.user_game_rating import UserGameRating

from app.routers import user, game, user_game_feedback, user_game_rating

from sqlalchemy import insert, select, update, delete

app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.get("/")
async def get_welcome(request: Request) -> HTMLResponse:
    return templates.TemplateResponse('welcome.html', {"request": request})


@app.get("/list_user")
async def get_list_user(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    users = db.scalars(select(User)).all()
    return templates.TemplateResponse('list_user.html', {"request": request, "users": users})


@app.get("/list_game")
async def get_list_game(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    games = db.scalars(select(Game)).all()
    return templates.TemplateResponse('list_games.html', {"request": request, "games": games})


@app.get("/list_game/{game_id}")
async def get_game(request: Request, db: Annotated[Session, Depends(get_db)], game_id: int) -> HTMLResponse:
    game = db.scalar(select(Game).where(Game.id == game_id))

    ratings_query = select(UserGameRating, User).join(User).where(UserGameRating.game_id == game_id)
    ratings = db.execute(ratings_query).all()

    feedbacks_query = select(UserGameFeedback, User).join(User).where(UserGameFeedback.game_id == game_id)
    feedbacks = db.execute(feedbacks_query).all()
    # ratings = db.scalars(select(UserGameRating).where(UserGameRating.game_id == game_id)).all()
    # feedbacks = db.scalars(select(UserGameFeedback).where(UserGameFeedback.game_id == game_id)).all()
    return templates.TemplateResponse('game.html', {"request": request,
                                                    "game": game,
                                                    "ratings": ratings,
                                                    "feedbacks": feedbacks})


@app.get("/list_user/{user_id}")
async def get_user(request: Request, db: Annotated[Session, Depends(get_db)], user_id: int) -> HTMLResponse:
    user = db.scalar(select(User).where(User.id == user_id))

    ratings_query = select(UserGameRating, Game).join(Game).where(UserGameRating.user_id == user_id)
    ratings = db.execute(ratings_query).all()

    feedbacks_query = (
        select(UserGameFeedback, Game)
        .join(Game)
        .where(UserGameFeedback.user_id == user_id)
    )
    feedbacks = db.execute(feedbacks_query).all()

    return templates.TemplateResponse('user.html', {
        "request": request,
        "user": user,
        "ratings": ratings,
        "feedbacks": feedbacks
    })


app.include_router(user.router_user)
app.include_router(game.router_game)
app.include_router(user_game_feedback.router_feedback)
app.include_router(user_game_rating.router_rating)

# @app.get("/list_user/{user_id}")
# async def get_user(request: Request, db: Annotated[Session, Depends(get_db)], user_id: int) -> HTMLResponse:
#     games = db.scalar(select(Game)).all()
#     user = db.scalar(select(User).where(User.id == user_id))
#     ratings = db.scalars(select(UserGameRating).where(UserGameRating.user_id == user_id)).all()
#     feedbacks = db.scalars(select(UserGameFeedback).where(UserGameFeedback.user_id == user_id)).all()
#     return templates.TemplateResponse('user.html', {"request": request,
#                                                     "user": user,
#                                                     "ratings": ratings,
#                                                     "feedbacks": feedbacks,
#                                                     "games": games})

# @app.get("/list_feedback")
# async def get_(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
#     feedbacks = db.scalars(select(UserGameFeedback)).all()
#     return templates.TemplateResponse('list_feedbacks.html', {"request": request, "feedbacks": feedbacks})
#
# @app.get("/list_rating")
# async def get_(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
#     ratings = db.scalars(select(UserGameRating)).all()
#     return templates.TemplateResponse('list_ratings.html', {"request": request, "ratings": ratings})
