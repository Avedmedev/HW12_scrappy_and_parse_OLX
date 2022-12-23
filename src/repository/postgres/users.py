from sqlalchemy import select

from src.repository.postgres.models import User


async def get_user_by_name(postgres, username):
    async with postgres as session:
        r = await session.execute(select(User).filter(User.login == username))
        result = r.scalars().first()
    return result
