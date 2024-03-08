from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    password_hash = Column(String)


class Word(Base):
    __tablename__ = "words"
    word_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    title = Column(String)
    translation = Column(String)


association_table2 = Table(
    "association_table_words_and_users",
    Base.metadata,
    Column("words", ForeignKey("words.word_id")),
    Column("users", ForeignKey("users.user_id"), unique=True),
)
