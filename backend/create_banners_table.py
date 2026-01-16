"""
Create homepage_banners table directly
Temporary workaround for migration issues
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    with open('create_banners_table.sql', 'r') as f:
        sql = f.read()

    conn.execute(text(sql))
    conn.commit()
    print("✅ Table homepage_banners created successfully!")

engine.dispose()
