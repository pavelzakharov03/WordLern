import uuid

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import app_settings
from db.models import User

engine = create_engine(app_settings.db)
SessionLocal = sessionmaker(bind=engine)

fake = Faker()


def seed_users():
    fake_users = [
        User(
            id=uuid.uuid4(),
            username=fake.name(),
            password_hash=str(hash(fake.password())),
        )
        for _ in range(100)
    ]
    with SessionLocal() as session:
        session.add_all(fake_users)
        session.commit()


if __name__ == "__main__":
    seed_users()
