from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import Base, engine
from .routers import (auth_router, users_router, services_router,
                      orders_router, reports_router)
from .services.payment_scheduler import (process_pending_payments,
                                         cleanup_finished_orders)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wash IS API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://192.168.1.5:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def auto_confirm_payments(request: Request, call_next):
    try:
        process_pending_payments()
        cleanup_finished_orders()
    except Exception as e:
        print(f"[scheduler] error: {e}")
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера",
                 "path": str(request.url)},
    )


app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(services_router.router)
app.include_router(orders_router.router)
app.include_router(reports_router.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "wash-is"}