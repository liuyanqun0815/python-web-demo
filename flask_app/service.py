from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from config import Settings
from models import User, UserMessage


class UserNotFoundError(Exception):
    pass


class ServiceValidationError(Exception):
    pass


@dataclass
class ProcessResult:
    user_id: int
    action: str
    age: int


engine = create_engine(Settings.database_url, pool_pre_ping=True, future=True)
session_factory = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False, future=True)


def calculate_age(birth_date: date, today: date) -> int:
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def process_user_message(user_id: int, message: str) -> ProcessResult:
    if not isinstance(user_id, int) or user_id <= 0:
        raise ServiceValidationError("user_id must be a positive integer")
    if not isinstance(message, str) or not message.strip():
        raise ServiceValidationError("message must be a non-empty string")

    try:
        with session_factory() as session:
            user = _get_user(session, user_id)
            if user is None:
                raise UserNotFoundError("user not found")

            action = _upsert_user_message(session, user_id, message.strip())
            user.age = calculate_age(user.birth_date, date.today())
            session.commit()

            return ProcessResult(
                user_id=user_id,
                action=action,
                age=user.age,
            )
    except SQLAlchemyError as exc:
        raise RuntimeError("database error") from exc


def _get_user(session: Session, user_id: int) -> User | None:
    statement = select(User).where(User.user_id == user_id)
    return session.scalar(statement)


def _upsert_user_message(session: Session, user_id: int, message: str) -> str:
    statement = select(UserMessage).where(UserMessage.user_id == user_id)
    user_message = session.scalar(statement)
    now = datetime.utcnow()

    if user_message is None:
        session.add(
            UserMessage(
                user_id=user_id,
                message=message,
                created_at=now,
                updated_at=now,
            )
        )
        return "inserted"

    user_message.message = message
    user_message.updated_at = now
    return "updated"
