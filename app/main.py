from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.campaigns import router as campaigns_router
from .routers.smtp import router as smtp_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
async def ping():
    return {"status": "ok"}


app.include_router(smtp_router)
app.include_router(campaigns_router)
