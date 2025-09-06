from fastapi import FastAPI
from app.router import router


app = FastAPI(title="Transcript Sentiment Analysis API")
app.include_router(router)
