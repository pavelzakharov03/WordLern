import uuid
from typing import Optional

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config.settings import app_settings
from db import models
from src.server.contracts import AuthAttributes, Token


class UsersRepo:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def login_user(self, auth_attributes: AuthAttributes) -> Optional[Token]:
        user = (
            self.db.query(models.User)
            .filter(models.User.user_name == auth_attributes.user_name)
            .first()
        )
        if user is not None and self.pwd_context.verify(
            auth_attributes.user_password.encode(), user.password_hash
        ):
            encoded_jwt = jwt.encode(
                {'user_id': str(user.user_id), 'user_name': user.user_name},
                app_settings.secret_key,
                algorithm='HS256',
            )
            return Token(token=encoded_jwt)
        return None

    def add_user(self, auth_attributes: AuthAttributes) -> Token:
        user = models.User(
            user_id=uuid.uuid4(),  # type: ignore
            user_name=auth_attributes.user_name,
            password_hash=self.pwd_context.hash(
                auth_attributes.user_password.encode()
            ),
        )
        self.db.add(user)
        encoded_jwt = jwt.encode(
            {'user_id': str(user.user_id), 'user_name': user.user_name},
            app_settings.secret_key,
            algorithm='HS256',
        )
        return Token(token=encoded_jwt)
