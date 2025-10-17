from fastapi import FastAPI

from .routers.campaigns import router as campaigns_router
from .routers.smtp import router as smtp_router

app = FastAPI()


@app.get("/ping")
async def ping():
    return {"status": "ok"}


app.include_router(smtp_router)
app.include_router(campaigns_router)
