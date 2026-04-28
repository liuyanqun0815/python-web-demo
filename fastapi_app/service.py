from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, UserMessage

logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    pass


class ServiceValidationError(Exception):
    pass


@dataclass
class ProcessResult:
    user_id: int
    action: str
    age: int


def calculate_age(birth_date: date, today: date) -> int:
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


async def process_user_message(session: AsyncSession, user_id: int, message: str) -> ProcessResult:
    if not isinstance(user_id, int) or user_id <= 0:
        raise ServiceValidationError("user_id must be a positive integer")
    if not isinstance(message, str) or not message.strip():
        raise ServiceValidationError("message must be a non-empty string")

    try:
        user = await _get_user(session, user_id)
        if user is None:
            raise UserNotFoundError("user not found")

        action = await _upsert_user_message(session, user_id, message.strip())
        user.age = calculate_age(user.birth_date, date.today())
        await session.commit()

        return ProcessResult(
            user_id=user_id,
            action=action,
            age=user.age,
        )
    except SQLAlchemyError as exc:
        await session.rollback()
        logger.exception("Database operation failed in process_user_message")
        raise RuntimeError(f"{exc.__class__.__name__}: {exc}") from exc


async def _get_user(session: AsyncSession, user_id: int) -> User | None:
    statement = select(User).where(User.user_id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def _upsert_user_message(session: AsyncSession, user_id: int, message: str) -> str:
    statement = select(UserMessage).where(UserMessage.user_id == user_id)
    result = await session.execute(statement)
    user_message = result.scalar_one_or_none()
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
