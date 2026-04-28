# 🔐 OAuth Login Project — FastAPI + Next.js + MySQL

A production-ready authentication system with **Google & GitHub OAuth**, built with **FastAPI (Python)** backend, **Next.js 15 (React)** frontend, and **MySQL** database.

---

## 📋 Features

✅ Google & GitHub OAuth 2.0 login  
✅ JWT-based authentication with `HttpOnly` secure cookies  
✅ MySQL database with SQLAlchemy ORM  
✅ Docker & Docker Compose support  
✅ Next.js 15 App Router with Server Components  
✅ TypeScript support  
✅ Hot reload for development  
✅ CSRF protection via OAuth `state` parameter *(recommended)*  

---

## 🗂️ Project Structure

```
oauth-login/
├── fastapi-auth/                 # 🔙 Backend (FastAPI + MySQL)
│   ├── docker-compose.yml        # Docker services (API + MySQL)
│   ├── Dockerfile                # FastAPI container config
│   ├── .env                      # Environment variables
│   ├── requirements.txt          # Python dependencies
│   ├── main.py                   # FastAPI app + OAuth routes
│   ├── test_db.py                # Database connection test
│   └── init.sql                  # Optional: database seed
│
├── my-frontend/                  # 🔜 Frontend (Next.js 15)
│   ├── app/
│   │   ├── layout.tsx            # Root layout + SessionProvider
│   │   ├── page.tsx              # Home page with login buttons
│   │   ├── dashboard/page.tsx    # Protected dashboard route
│   │   ├── lib/auth.ts           # Server-side session helper
│   │   └── components/auth-buttons.tsx  # OAuth login buttons
│   ├── .env.local                # Frontend environment vars
│   ├── next.config.ts            # Next.js config
│   └── package.json              # Node dependencies
│
├── README.md                     # This file
└── .gitignore                    # Git ignore rules
```

---

## 🚀 Quick Start (Docker Compose — Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with WSL 2 backend on Windows)
- [Git](https://git-scm.com/)

### 1️⃣ Clone & Navigate
```bash
git clone <your-repo>
cd oauth-login/fastapi-auth
```

### 2️⃣ Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your OAuth credentials (see "Environment Variables" below)
code .env  # or use any editor
```

### 3️⃣ Start Services
```bash
# Build and start MySQL + FastAPI
docker-compose up --build

# Or run in background:
docker-compose up -d --build
```

✅ Wait for:  
```
fastapi-oauth  | INFO: Uvicorn running on http://0.0.0.0:8000
```

### 4️⃣ Verify Backend
- Open: http://localhost:8000/docs → Swagger UI loads ✅
- Test OAuth: Click "Execute" on `GET /auth/google`

### 5️⃣ Start Frontend
```bash
cd ../my-frontend
npm install
npm run dev
```

✅ Visit: http://localhost:3000 → Click "Login with Google/GitHub"

---

## ⚙️ Manual Setup (Without Docker)

### 🔙 Backend (FastAPI + MySQL)

#### 1. Install MySQL
- **Option A (Docker)**:
  ```bash
  docker run -d --name mysql-oauth \
    -e MYSQL_ROOT_PASSWORD=root \
    -e MYSQL_DATABASE=auth_db \
    -p 3306:3306 mysql:8
  ```
- **Option B (Local)**: Install from https://dev.mysql.com/downloads/installer/

#### 2. Setup Python Environment
```bash
cd fastapi-auth
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# or: venv\Scripts\activate  # Windows CMD

pip install -r requirements.txt
```

#### 3. Configure `.env`
```env
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
JWT_SECRET=your_strong_secret_min_32_chars!!
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/auth_db

# OAuth credentials (get from provider consoles)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

#### 4. Run Server
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

✅ Verify: http://localhost:8000/docs

---

### 🔜 Frontend (Next.js 15)

#### 1. Create App
```bash
npx create-next-app@latest my-frontend --typescript --tailwind --app
cd my-frontend
```

#### 2. Install Dependencies
```bash
npm install @auth/nextjs @auth/core  # Optional: if using Auth.js
# Or use manual cookie-based auth (as in this project)
```

#### 3. Configure `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 4. Add Auth Files
Copy the frontend files from this repo into `my-frontend/`:
- `app/lib/auth.ts`
- `app/components/auth-buttons.tsx`
- `app/dashboard/page.tsx`
- `app/page.tsx`
- `app/layout.tsx` (wrap with SessionProvider if needed)

#### 5. Run Dev Server
```bash
npm run dev
```

✅ Visit: http://localhost:3000

---

## 🔑 Environment Variables Reference

### Backend (`fastapi-auth/.env`)
| Variable | Description | Example |
|----------|-------------|---------|
| `APP_URL` | Frontend URL (for redirects) | `http://localhost:3000` |
| `API_URL` | Backend URL (for OAuth callbacks) | `http://localhost:8000` |
| `JWT_SECRET` | Secret for signing JWTs (min 32 chars) | `openssl rand -base64 32` |
| `DATABASE_URL` | SQLAlchemy MySQL connection string | `mysql+pymysql://user:pass@host:3306/db` |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `123456.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | `GOCSPX-abc123` |
| `GITHUB_CLIENT_ID` | GitHub OAuth Client ID | `Iv1.abc123` |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth Client Secret | `ghs_abc123` |
| `NODE_ENV` | `development` or `production` (controls cookie `secure` flag) | `development` |

### Frontend (`my-frontend/.env.local`)
| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

> 🔐 **Never commit `.env` files**! Add to `.gitignore`:
> ```gitignore
> .env
> .env.local
> *.log
> __pycache__/
> node_modules/
> venv/
> ```

---

## 🔐 OAuth Provider Setup

### 🟦 Google Cloud Console
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create **OAuth 2.0 Client ID** → Web application
3. **Authorized redirect URIs** (add BOTH):
   ```
   http://localhost:8000/auth/google/callback          # Local dev
   https://api.yourdomain.com/auth/google/callback     # Production
   ```
4. Copy **Client ID** and **Client Secret** → Paste into `.env`

### 🐙 GitHub Developer Settings
1. Go to: https://github.com/settings/developers
2. **New OAuth App**
3. **Authorization callback URL**:
   ```
   http://localhost:8000/auth/github/callback          # Local dev
   https://api.yourdomain.com/auth/github/callback     # Production
   ```
4. Copy **Client ID** and generate **Client Secret** → Paste into `.env`

> ⚠️ **Critical**: Redirect URIs must match **exactly** (no trailing slashes, http/https, port numbers).

---

## 🌐 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/auth/google` | Redirect to Google login |
| `GET` | `/auth/google/callback` | Google OAuth callback (internal) |
| `GET` | `/auth/github` | Redirect to GitHub login |
| `GET` | `/auth/github/callback` | GitHub OAuth callback (internal) |
| `GET` | `/logout` | Clear auth cookie & redirect to frontend |

### Protected Routes
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| `GET` | `/api/me` | Get current user info | ✅ Yes |

### Example: Fetch User Info (Frontend)
```ts
// Server Component (Next.js App Router)
import { cookies } from "next/headers";

const cookieStore = await cookies();
const token = cookieStore.get("token")?.value;

const res = await fetch("http://localhost:8000/api/me", {
  headers: { Cookie: `token=${token}` }
});
const user = await res.json();
```

---

## 🧪 Testing

### Backend
```bash
# Test database connection
cd fastapi-auth
python test_db.py

# Test API with curl
curl -I http://localhost:8000/docs
curl http://localhost:8000/auth/google  # Should redirect to Google
```

### Frontend
```bash
cd my-frontend
npm run dev
# Visit http://localhost:3000 and click login buttons
```

### Full Flow Test
1. Visit `http://localhost:3000`
2. Click "Login with Google"
3. Approve in Google popup
4. Redirected to `http://localhost:3000/dashboard` ✅
5. See user email & provider info

---

## 🐳 Docker Commands Reference

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f api
docker-compose logs -f mysql

# Stop services
docker-compose down

# Stop + remove volumes (⚠️ deletes DB data)
docker-compose down -v

# Exec into API container
docker-compose exec api bash

# Exec into MySQL
docker-compose exec mysql mysql -u appuser -p auth_db

# Run one-off command in API container
docker-compose run api python test_db.py
```

---

## 🛠️ Troubleshooting

### ❌ `redirect_uri_mismatch` (Google/GitHub)
✅ Fix: Ensure `.env` `API_URL` matches **exactly** what's registered in provider console:
```env
# ✅ Correct
API_URL=http://localhost:8000
# → redirect_uri = http://localhost:8000/auth/google/callback

# ❌ Wrong (trailing slash)
API_URL=http://localhost:8000/
# → redirect_uri = http://localhost:8000//auth/google/callback
```

### ❌ MySQL connection failed
✅ Fixes:
- Use `127.0.0.1` instead of `localhost` in `DATABASE_URL` (Windows Docker)
- Wait 30s for MySQL to initialize after `docker run`
- Check logs: `docker logs mysql-oauth`
- Test manually: `mysql -h 127.0.0.1 -u root -p`

### ❌ CORS errors
✅ Fix: Ensure backend `main.py` has:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("APP_URL")],  # Must match frontend URL exactly
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### ❌ Cookie not set / auth not persisting
✅ Fixes:
- In dev: `secure=False` on cookies (set via `is_prod` flag)
- In prod: Use `https://` and set `secure=True`
- Ensure `SameSite=Lax` (allows cross-site redirect from OAuth provider)

### ❌ Next.js 15 `cookies()` error
✅ Fix: `cookies()` is async in Next.js 15+:
```ts
// ✅ Correct
const cookieStore = await cookies();
const token = cookieStore.get("token")?.value;
```

---

## 🚀 Production Deployment

### Backend (Render / Railway / Fly.io)
1. Push `fastapi-auth/` to GitHub
2. Create new Web Service
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all `.env` variables
6. Set `API_URL=https://your-api.onrender.com`

### Frontend (Vercel)
1. Push `my-frontend/` to GitHub
2. Import to Vercel
3. Add env: `NEXT_PUBLIC_API_URL=https://your-api.onrender.com`
4. Deploy (auto-detects Next.js)

### Database (PlanetScale / AWS RDS / Railway MySQL)
1. Create managed MySQL instance
2. Get connection string → Update `DATABASE_URL`
3. Run migrations (use Alembic in production)

### Final Production Checklist
- [ ] Use `https://` everywhere
- [ ] Set `JWT_SECRET` to strong random value
- [ ] Enable `secure=True` on cookies
- [ ] Add production redirect URIs to Google/GitHub consoles
- [ ] Set up database backups
- [ ] Add rate limiting to `/auth/callback` endpoints
- [ ] Monitor logs & errors (Sentry, Logflare, etc.)

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feat/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feat/amazing-feature`
5. Open Pull Request

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 💬 Support

Found a bug? Have a question?  
👉 Open an [Issue](https://github.com/yourusername/oauth-login/issues) or start a [Discussion](https://github.com/yourusername/oauth-login/discussions)

---

> ✨ **Pro Tip**: Bookmark this README! Run `docker-compose up` and you're 90% there. 🚀

**Happy coding!** 🔐🐍⚛️