from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.tasks import save_user_async

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ─── SYNC ────────────────────────────────────────────────────────────────────

@router.get("/sync", response_class=HTMLResponse)
async def show_sync_form(request: Request):
    return templates.TemplateResponse(request=request, name="form_sync.html")


@router.post("/sync")
async def submit_sync_form(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    first_name = first_name.strip()
    last_name = last_name.strip()

    if not first_name or not last_name:
        return templates.TemplateResponse(
            request=request,
            name="form_sync.html",
            context={"error": "Imię i nazwisko są wymagane."},
            status_code=422,
        )

    user = User(first_name=first_name, last_name=last_name, source="sync")
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return RedirectResponse(url=f"/success?mode=sync&user_id={user.id}", status_code=303)


# ─── ASYNC ───────────────────────────────────────────────────────────────────

@router.get("/async", response_class=HTMLResponse)
async def show_async_form(request: Request):
    return templates.TemplateResponse(request=request, name="form_async.html")


@router.post("/async")
async def submit_async_form(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
):
    first_name = first_name.strip()
    last_name = last_name.strip()

    if not first_name or not last_name:
        return templates.TemplateResponse(
            request=request,
            name="form_async.html",
            context={"error": "Imię i nazwisko są wymagane."},
            status_code=422,
        )

    # Wysyłamy do kolejki Celery — odpowiedź jest natychmiastowa
    task = save_user_async.delay(first_name, last_name)

    return RedirectResponse(
        url=f"/success?mode=async&task_id={task.id}",
        status_code=303,
    )
