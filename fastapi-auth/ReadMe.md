DATABASE_URL=mysql+pymysql://root:root@localhost:3306/auth_db

uvicorn main:app --reload --port 8000