import uuid

import jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient
from psycopg2.errors import lookup

from config.settings import app_settings
from db.users import UsersRepo
from db.models import User
from src.server.server import app
from src.server.contracts import Token

client = TestClient(app)


def test_register_happy_path(mocker) -> None:  # type: ignore
    mocker_value = User(
        user_id=uuid.UUID(
            '74f3cde6-0c2d-4222-8b60-6ede5d0a661a'
        ),  # type: ignore
        user_name='Andrei',
        password_hash='\x243262243132245249776858453350637a4c714'
        '643633446726f4945654849355a6a793664393543'
        '58464467796e4e78557863774b545a4338317632',
    )

    mocker.patch.object(Session, "add", return_value=mocker_value)

    response = client.post(
        "/register", json={'user_name': 'Andrei', 'user_password': 'Hihi'}
    )
    assert response.status_code == 200
    assert response.json().get('token') is not None


def test_authorization_happy_path(mocker) -> None:  # type: ignore
    encoded_jwt = jwt.encode(
        {
            'user_id': '74f3cde6-0c2d-4222-8b60-6ede5d0a661a',
            'user_name': 'Andrei',
        },
        app_settings.secret_key,
        algorithm='HS256',
    )
    mocker_value = Token(token=encoded_jwt)
    mocker.patch.object(UsersRepo, "login_user", return_value=mocker_value)

    response = client.post(
        "/auth", json={'user_name': 'Andrei', 'user_password': 'Hihi'}
    )
    assert response.status_code == 200
    assert response.json() == {'token': encoded_jwt}


def test_register_account_already_exists(mocker) -> None:  # type: ignore
    mocker.patch.object(
        Session,
        "add",
        side_effect=IntegrityError(
            statement='INSERT INTO users (user_id, user_name, password_hash) '
            'VALUES (%(user_id)s::UUID, %(user_name)s, %(password_hash)s) )',
            orig=lookup('23505'),  # type: ignore
            params={
                'user_id': uuid.UUID('1b91138a-5de7-4c78-97fa-7d8d8ad5e595'),
                'user_name': 'Andrei',
                'password_hash': b'$2b$12$i6aWPnv1c8HbmJmBWxxHi.'
                b'kVNGkJBRw2asaSjWwObsJ4ECLik4MBe',
            },
        ),
    )
    response = client.post(
        "/register", json={'user_name': 'Andrei', 'user_password': 'Hihi'}
    )
    assert response.status_code == 409
    assert response.json() == {'detail': 'Account already exists'}
