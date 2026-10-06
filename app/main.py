from fastapi import FastAPI

from app.routers import cars

app = FastAPI(title="Cars API")
app.include_router(cars.router)