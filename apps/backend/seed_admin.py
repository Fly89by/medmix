import asyncio
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import User
from sqlalchemy import select


async def seed():
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.email == "admin@medmix.com"))
        if result.scalar_one_or_none():
            print("Admin user already exists")
            return

        user = User(
            name="Admin",
            email="admin@medmix.com",
            password_hash=hash_password("admin123"),
            role="ADMIN",
        )
        db.add(user)
        await db.commit()
        print("Admin user created: admin@medmix.com / admin123")


asyncio.run(seed())
