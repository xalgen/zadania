from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@router.get("/success", response_class=HTMLResponse)
async def success(
    request: Request,
    mode: str = "sync",
    task_id: str = None,
    user_id: int = None,
):
    return templates.TemplateResponse(
        request=request,
        name="success.html",
        context={"mode": mode, "task_id": task_id, "user_id": user_id},
    )


@router.get("/task-status/{task_id}")
async def task_status(task_id: str):
    """Sprawdź status zadania Celery — zwraca JSON."""
    from app.tasks import celery_app

    task = celery_app.AsyncResult(task_id)
    return {"task_id": task_id, "status": task.status, "result": task.result}
