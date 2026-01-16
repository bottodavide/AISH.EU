"""
Create consulting_packages table directly
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    with open('create_packages_table.sql', 'r') as f:
        sql = f.read()

    conn.execute(text(sql))
    conn.commit()
    print("✅ Tables consulting_packages and package_services created successfully!")

engine.dispose()
