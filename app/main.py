from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from app.config import get_settings
from app.db.session import session_scope
from app.exceptions import register_exception_handlers
from app.landing import public_base_url, render_landing
from app.routers import projects, tasks, users

settings = get_settings()

# The Task 3 brief's requirements, each mapped to where it is met — shown on
# the landing page and verifiable there with "Run live checks".
TASK_REQUIREMENTS = [
    ("User data storage", "PostgreSQL users table. Email has a unique index; passwords are stored as PBKDF2 hashes."),
    ("Project data storage", "projects table, with an owner_id foreign key to users."),
    ("Task data storage", "tasks table, with a native Postgres enum for status and a project_id foreign key."),
    ("Full CRUD across all entities", "Create, read, update and delete for users, projects and tasks."),
    ("Validation at the database / schema level", "NOT NULL, length limits, the unique email index, foreign keys and the status enum are enforced by Postgres itself. Tests bypass the API to prove it."),
    ("Relationships between users, projects and tasks", "users → projects → tasks, with ON DELETE CASCADE on both foreign keys."),
    ("Secure database configuration", "DATABASE_URL comes from the environment. No credentials are committed."),
    ("Schema and models in the repository", "SQLAlchemy models (app/db/models.py), Alembic migrations, and an ER diagram in the README."),
]

app = FastAPI(
    title="Users, Projects & Tasks API",
    description="Task 3 — Innovation Hacks Full Stack Development Internship",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/health", tags=["health"], summary="Service and database health check")
def health_check(response: Response) -> dict[str, str]:
    try:
        with session_scope() as session:
            session.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        database = "unavailable"
        response.status_code = 503
    return {
        "status": "ok" if database == "ok" else "degraded",
        "environment": settings.app_env,
        "database": database,
    }


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
def landing_page(request: Request) -> HTMLResponse:
    base = public_base_url(request.headers.get("host", "localhost"), request.url.scheme)
    return HTMLResponse(
        render_landing(
            app,
            base_url=base,
            environment=settings.app_env,
            repo_url="https://github.com/Aime-Serge/innovation-hacks-task3-api-db-integration",
            label="Task 3",
            requirements=TASK_REQUIREMENTS,
        )
    )
