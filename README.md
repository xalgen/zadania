
## Zadanie 1 — Flask

Serwis oparty na frameworku Flask z dwoma trybami obsługi formularza zbierającego dane użytkownika (imię i nazwisko).

**Tryb synchroniczny** — dane przesyłane są POST requestem i zapisywane bezpośrednio do bazy SQLite w trakcie obsługi żądania. Użytkownik czeka na odpowiedź serwera.

**Tryb asynchroniczny** — dane trafiają do kolejki Celery z brokerem Redis (Upstash). Worker przetwarza zadanie w tle, a użytkownik otrzymuje odpowiedź natychmiast po kolejkowaniu.

**Stos:** Flask, SQLAlchemy, SQLite, Celery, Redis (Upstash)

**Uruchomienie:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Terminal 1
python run.py

# Terminal 2
celery -A celery_worker.celery worker --loglevel=info
```

---

## Zadanie 2 — FastAPI

Przepisanie logiki z Zadania 1 na framework FastAPI z zachowaniem tych samych funkcjonalności.

Kluczowe różnice względem Flaska:
- FastAPI działa w modelu ASGI (async-first), Flask domyślnie WSGI
- Walidacja danych przez Pydantic zamiast ręcznej weryfikacji
- Automatyczna dokumentacja API dostępna pod `/docs`
- Async SQLAlchemy z `aiosqlite` dla operacji bazodanowych
- Celery worker używa osobnego synchronicznego engine SQLAlchemy (Celery nie obsługuje asyncio natywnie)

**Stos:** FastAPI, Uvicorn, SQLAlchemy async, aiosqlite, Celery, Redis (Upstash)

**Uruchomienie:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Terminal 1
uvicorn main:app --reload --port 8000

# Terminal 2
celery -A celery_worker.celery_app worker --loglevel=info
```

Dokumentacja API: `http://localhost:8000/docs`

---

## Zadanie 3 — Deployment na GCP + testy wydajności

Aplikacje z Zadań 1 i 2 zostały wdrożone na instancję GCP (Debian, e2-micro) z Nginx jako reverse proxy.

### Przetestowane warianty

**Wariant 1 — Flask + Gunicorn (WSGI) + Nginx**
Klasyczne podejście WSGI. Gunicorn zarządza pulą synchronicznych workerów. Nginx przekazuje ruch przez Unix socket.

**Wariant 2 — Flask + Uvicorn (ASGI) + Nginx**
Flask opakowany przez `asgiref.WsgiToAsgi` i serwowany przez Uvicorn. Umożliwia obsługę połączeń w modelu asynchronicznym mimo synchronicznej natury Flaska.

**Wariant 3 — FastAPI + Uvicorn (ASGI) + Nginx**
Natywne środowisko dla FastAPI. Uvicorn obsługuje async event loop bezpośrednio, bez warstwy pośredniej.

### Wyniki testów k6

Testy przeprowadzone narzędziem k6 z profilem obciążenia: ramp-up 0→10 VU (30s), plateau 50 VU (60s), ramp-down (30s).

| Wariant | p(95) | Błędy | Avg response |
|---|---|---|---|
| Flask WSGI | 10.93ms | 0.00% | 9.95ms |
| Flask ASGI | ~10ms | 0.00% | ~9ms |
| FastAPI ASGI | 9.77ms | 0.11% | 8.2ms |

Wszystkie warianty zmieściły się w założonym progu `p(95) < 500ms`. Trzy błędy przy FastAPI to timeout podczas spike'u spowodowany ograniczeniami RAM instancji (1 GB). Na większej maszynie wynik byłby czysty.

### Konfiguracja serwera

```
Nginx → Unix socket → Gunicorn/Uvicorn → Aplikacja
```

Każdy serwis uruchomiony jako jednostka systemd z `Restart=always` — aplikacje wznawiane automatycznie po restarcie serwera.

**Działające endpointy:**
- `http://34.116.177.90/` — Flask WSGI
- `http://34.116.177.90/asgi/` — Flask ASGI
- `http://34.116.177.90/fastapi/` — FastAPI ASGI

---

## Zadanie 4 — Ochrona przed botami

Formularz zabezpieczony trzema warstwami ochrony, dobranymi pod kątem skuteczności i zerowego wpływu na doświadczenie prawdziwego użytkownika.

### Warstwa 1 — Honeypot

Ukryte pole `website` niewidoczne dla użytkownika (CSS `display:none`). Bot wypełniający formularz automatycznie uzupełnia to pole — serwer wykrywa to i zwraca pozorny sukces bez zapisywania danych. Zatrzymuje większość prostych botów bez żadnego friction dla użytkownika.

### Warstwa 2 — Rate Limiting (Flask-Limiter)

Limit 5 requestów POST na minutę per adres IP. Blokuje masowe ataki nawet jeśli bot ominął honeypot. Przy przekroczeniu limitu serwer zwraca `429 Too Many Requests`.

### Warstwa 3 — CSRF Token (Flask-WTF)

Każdy formularz zawiera ukryty token generowany po stronie serwera. Żądania POST bez ważnego tokenu są odrzucane. Chroni przed atakami Cross-Site Request Forgery, gdzie złośliwa strona próbuje wysłać formularz w imieniu użytkownika.

---

## Struktura repozytoriów

```
zadanie1_flask/     — Flask + SQLite + Celery
zadanie2_fastapi-/  — FastAPI + async SQLAlchemy + Celery
zadanie4/           — Flask + anti-bot (honeypot + rate limiting + CSRF)
```

## Zmienne środowiskowe

Każdy projekt wymaga pliku `.env`:

```env
UPSTASH_REDIS_URL=rediss://:PASSWORD@HOSTNAME:PORT
SECRET_KEY=twoj-tajny-klucz
```

Redis dostarczany przez [Upstash](https://upstash.com) — darmowy tier bez konieczności stawiania własnej instancji.
