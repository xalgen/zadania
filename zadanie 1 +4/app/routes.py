from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import User
from app.tasks import save_user_async
from app import db, limiter
main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


# ─── FORMULARZ SYNCHRONICZNY ─────────────────────────────────────────────────

@main.route("/sync", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def form_sync():
    if request.method == "POST":
        # Warstwa 1: Honeypot — bot wypełnił ukryte pole
        honeypot = request.form.get("website", "")
        if honeypot:
            # Silent fail — udajemy sukces żeby nie edukować bota
            flash("Zapisano pomyślnie.", "success")
            return redirect(url_for("main.success", mode="sync"))

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()

        if not first_name or not last_name:
            flash("Imię i nazwisko są wymagane.", "error")
            return redirect(url_for("main.form_sync"))

        user = User(first_name=first_name, last_name=last_name, source="sync")
        db.session.add(user)
        db.session.commit()

        flash(f"Zapisano: {first_name} {last_name} (synchronicznie)", "success")
        return redirect(url_for("main.success", mode="sync"))

    return render_template("form_sync.html")


# ─── FORMULARZ ASYNCHRONICZNY ─────────────────────────────────────────────────

@main.route("/async", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def form_async():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()

        if not first_name or not last_name:
            flash("Imię i nazwisko są wymagane.", "error")
            return redirect(url_for("main.form_async"))

        # Zapis asynchroniczny — wysyłamy task do kolejki i natychmiast zwracamy odpowiedź
        task = save_user_async.delay(first_name, last_name)

        flash(
            f"Zadanie dodane do kolejki (ID: {task.id}). Dane zostaną zapisane asynchronicznie.",
            "success"
        )
        return redirect(url_for("main.success", mode="async", task_id=task.id))

    return render_template("form_async.html")


@main.route("/success")
def success():
    mode = request.args.get("mode", "sync")
    task_id = request.args.get("task_id")
    return render_template("success.html", mode=mode, task_id=task_id)


@main.route("/task-status/<task_id>")
def task_status(task_id: str):
    """Opcjonalny endpoint do sprawdzenia statusu taska Celery (AJAX polling)."""
    from app import celery
    task = celery.AsyncResult(task_id)
    return {"task_id": task_id, "status": task.status, "result": task.result}
