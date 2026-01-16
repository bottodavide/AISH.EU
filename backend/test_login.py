import asyncio
from app.core.security import verify_password
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserProfile

async def test_login():
    email = "admin@aistrategyhub.eu"
    password = "Test123!"
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print("User not found")
            return
            
        # Verify password
        if not verify_password(password, user.password_hash):
            print("Password incorrect")
            return
        
        print("Login successful!")
        print(f"\nUser data that should be returned:")
        print(f"  email: {user.email}")
        print(f"  role: {user.role.value}")
        print(f"  is_active: {user.is_active}")
        print(f"  is_email_verified: {user.is_email_verified}")
        
        # Load profile
        profile_result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )
        profile = profile_result.scalar_one_or_none()
        
        if profile:
            print(f"\nProfile data:")
            print(f"  first_name: {profile.first_name}")
            print(f"  last_name: {profile.last_name}")
            print(f"  company_name: {profile.company_name}")
        else:
            print("\nNo profile found")

asyncio.run(test_login())
