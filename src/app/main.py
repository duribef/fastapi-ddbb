from fastapi import FastAPI
import app.services as _services

app = FastAPI()

# Create tables
_services._add_tables()

@app.get("/")
async def root():
    return {"message": "Hello World"}