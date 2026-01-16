import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User

async def check_admin():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == 'admin@aistrategyhub.eu')
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Role value: {user.role.value}")
            print(f"Is active: {user.is_active}")
            print(f"Is verified: {user.is_email_verified}")
        else:
            print("User admin@aistrategyhub.eu not found in database")
            
        # List all users
        print("\nAll users:")
        all_users = await db.execute(select(User))
        for u in all_users.scalars().all():
            print(f"  - {u.email}: {u.role.value}")

asyncio.run(check_admin())
