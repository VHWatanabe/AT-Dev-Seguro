from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.routes import consultas, paginas, auth, admin, laboratorio
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.rate_limit import limiter
from app.database.database import init_db

app = FastAPI(title="API de Agendamento de Consultas")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router)
app.include_router(consultas.router)
app.include_router(paginas.router)
app.include_router(admin.router)
app.include_router(laboratorio.router)


@app.get("/")
def root():
    return {"status": "ok"}