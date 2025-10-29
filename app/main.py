from fastapi import FastAPI
from app.database import Base, engine
from app.routes import rates, differences

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Currency Monitor")

app.include_router(rates.router)
app.include_router(differences.router)   
