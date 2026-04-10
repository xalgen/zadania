from app import celery, db
from app.models import User

@celery.task(name="tasks.save_user_async")
def save_user_async(first_name: str, last_name: str) -> dict:
    """
    Zadanie asynchroniczne: zapisuje użytkownika do bazy.
    Wykonuje się w osobnym procesie workera Celery.
    """
    user = User(first_name=first_name, last_name=last_name, source="async")
    db.session.add(user)
    db.session.commit()
    return {"status": "saved", "user": f"{first_name} {last_name}"}
