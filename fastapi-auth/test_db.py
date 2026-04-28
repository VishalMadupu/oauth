from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
print(f"🔗 Connecting to: {DB_URL}")

engine = create_engine(DB_URL)
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DATABASE();"))
        db_name = result.fetchone()[0]
        print(f"✅ Success! Connected to database: {db_name}")
except Exception as e:
    print(f"❌ Failed: {e}")
    print("💡 Tip: Check if MySQL container is running: docker ps")