from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))  # ✅ use text()
        print("✅ Connected successfully!")
        print("PostgreSQL version:", result.scalar())  # scalar() extracts single value
except Exception as e:
    print("❌ Connection failed:")
    print(e)
