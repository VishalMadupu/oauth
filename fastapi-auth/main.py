import os
import httpx
from jose import jwt 
import datetime
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ================= CONFIG =================
APP_URL = os.getenv("APP_URL", "http://localhost:3000")
API_URL = os.getenv("API_URL", "http://localhost:8000")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretdevkey")
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
is_prod = os.getenv("NODE_ENV") == "production"

# ================= DATABASE =================
# Create SQLAlchemy engine. Use a sqlite fallback for local development.
if DB_URL.startswith("sqlite"):
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255))
    provider = Column(String(50))
    provider_id = Column(String(255))

# Create tables on startup (Use Alembic in production)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= APP =================
app = FastAPI(title="OAuth Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[APP_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_token(user_id: int, email: str) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    return jwt.encode({"sub": user_id, "email": email, "exp": expire}, JWT_SECRET, algorithm="HS256")

async def verify_token(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ================= AUTH ROUTES =================
@app.get("/auth/google")
def auth_google():
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": f"{API_URL}/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile"
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url=f"https://accounts.google.com/o/oauth2/v2/auth?{qs}")

@app.get("/auth/github")
def auth_github():
    params = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "redirect_uri": f"{API_URL}/auth/github/callback",
        "scope": "user:email"
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url=f"https://github.com/login/oauth/authorize?{qs}")

@app.get("/auth/google/callback")
async def google_callback(request: Request, db=Depends(get_db)):
    code = request.query_params.get("code")
    if not code: raise HTTPException(400, "Missing code")

    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://oauth2.googleapis.com/token", data={
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{API_URL}/auth/google/callback"
        })
        if token_res.status_code != 200:
            raise HTTPException(400, "Google token exchange failed")
        access_token = token_res.json().get("access_token")

        user_res = await client.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        user_data = user_res.json()

    email = user_data.get("email")
    if not email: raise HTTPException(400, "Google did not return an email")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=user_data.get("name"), provider="google", provider_id=user_data["sub"])
        db.add(user)
        db.commit()
        db.refresh(user)

    response = RedirectResponse(url=f"{APP_URL}/dashboard")
    response.set_cookie("token", create_token(user.id, user.email), httponly=True, secure=is_prod, samesite="lax", max_age=604800)
    return response

@app.get("/auth/github/callback")
async def github_callback(request: Request, db=Depends(get_db)):
    code = request.query_params.get("code")
    if not code: raise HTTPException(400, "Missing code")

    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://github.com/login/oauth/access_token", data={
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "code": code,
            "redirect_uri": f"{API_URL}/auth/github/callback"
        }, headers={"Accept": "application/json"})
        if token_res.status_code != 200:
            raise HTTPException(400, "GitHub token exchange failed")
        access_token = token_res.json().get("access_token")

        user_res = await client.get("https://api.github.com/user", headers={"Authorization": f"token {access_token}"})
        user_data = user_res.json()

    email = user_data.get("email")
    if not email:
        # Fallback if primary email is private
        email_res = await client.get("https://api.github.com/user/emails", headers={"Authorization": f"token {access_token}"})
        emails = [e for e in email_res.json() if e["primary"] and e["verified"]]
        email = emails[0]["email"] if emails else f"{user_data['login']}@github.placeholder"

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=user_data.get("name"), provider="github", provider_id=str(user_data["id"]))
        db.add(user)
        db.commit()
        db.refresh(user)

    response = RedirectResponse(url=f"{APP_URL}/dashboard")
    response.set_cookie("token", create_token(user.id, user.email), httponly=True, secure=is_prod, samesite="lax", max_age=604800)
    return response

@app.get("/api/me")
def get_me(payload: dict = Depends(verify_token)):
    return {"id": payload["sub"], "email": payload["email"]}

@app.get("/logout")
def logout():
    res = RedirectResponse(url=APP_URL)
    res.delete_cookie("token", secure=is_prod)
    return res