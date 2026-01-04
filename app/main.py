from fastapi import FastAPI
from .database import Base, engine
from .routes import router

from dotenv import load_dotenv



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment API")

app.include_router(router)

load_dotenv()
