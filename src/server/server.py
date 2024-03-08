from typing import Any
import logging.config

import jwt
from fastapi import FastAPI, HTTPException, Header, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from config.settings import app_settings
from db.words_repo import WordsRepo
from db.users import UsersRepo
from src.server.contracts import Token, AuthAttributes, WordContract
from src.word import word_client

app = FastAPI()

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": app_settings.log_level,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": app_settings.log_level,
    },
}

logging.config.dictConfig(logging_config)

engine = create_engine(app_settings.db)
SessionLocal = sessionmaker(autoflush=False, bind=engine)


@app.post("/auth", response_model=Token)
async def authorization(
    auth_attributes: AuthAttributes,
) -> HTTPException | Token:
    try:
        with SessionLocal() as session:
            users_table = UsersRepo(session)
            token = users_table.login_user(auth_attributes)
            if token is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return token
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from error


@app.post("/register", response_model=Token)
async def register(auth_attributes: AuthAttributes) -> Token | None:
    try:
        with SessionLocal() as session:
            users_table = UsersRepo(session)
            token = users_table.add_user(auth_attributes)
            session.commit()
        return token
    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from error


def login(token: str | None) -> Any | None:
    if token is None:
        return None
    try:
        user_data = jwt.decode(token, app_settings.secret_key, ["HS256"])
        return user_data
    except jwt.exceptions.InvalidTokenError:
        return None


@app.get("/word", response_model=WordContract)
def get_word(token: str = Header(None)) -> WordContract | None:
    user_data = login(token)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
        )
    resp = word_client.get_word_and_translate()
    with SessionLocal() as session:
        wrs = WordsRepo(session)
        wrs.add_word(resp[0], resp[1])
        wrs.add_last_word(resp[0], user_data["user_id"])
    return WordContract(word=resp[0])


@app.post("/word", response_model=WordContract)
def post_word_translate(
    word_translation: str,
    token: str = Header(None),
) -> WordContract | None:
    user_data = login(token)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
        )
    with SessionLocal() as session:
        wrs = WordsRepo(session)
        last_word = wrs.get_user_last_word(user_data["user_id"])
        if last_word is None:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="first run a get query to get the word",
            )
        wrs.get_word(last_word)
        if word_client.assert_word(
            wrs.get_translation_by_word_title(last_word), word_translation
        ):
            resp = word_client.get_word_and_translate()
            with SessionLocal() as session:
                wrs = WordsRepo(session)
                wrs.add_word(resp[0], resp[1])
                session.commit()
                wrs.add_last_word(resp[0], user_data["user_id"])
                return WordContract(word=resp[0])

        return WordContract(word=last_word)
