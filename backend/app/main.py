from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.routes import router
from app.api.workflow import router as workflow_router
from app.core.config import settings
from app.db.session import init_db
from app.landing import render_landing
from app.scripts.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed(force=False)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Healthcare AI Workflow Assistant",
        version="0.2.0",
        description=(
            "Synthetic healthcare note assistant with structured extraction, "
            "human review workflow, audit logging, and demo dashboard."
        ),
        lifespan=lifespan,
    )
    app.include_router(router, prefix=settings.api_prefix)
    app.include_router(workflow_router, prefix=settings.api_prefix)

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name}

    @app.get("/", response_class=HTMLResponse)
    def landing_page() -> str:
        return render_landing(
            "Healthcare AI Workflow Assistant",
            "Production-style portfolio API — structured AI extraction, human review, audit logging.",
            "Not for real patient data or clinical decision-making. Demo notes only.",
            "healthcare-ai-workflow-assistant",
            extra_links=[("/dashboard", "Review dashboard")],
            quick_steps=[
                'Check <a href="/health">/health</a>',
                'Open <a href="/dashboard">/dashboard</a> — seeded review queue',
                'Create a note via <code>POST /api/v1/notes</code> in <a href="/docs">/docs</a>',
                "Run extraction then review with <code>POST /api/v1/extractions/{id}/review</code>",
            ],
        )

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard() -> str:
        template_path = Path(__file__).parent / "static" / "dashboard.html"
        return template_path.read_text(encoding="utf-8")

    return app


app = create_app()
