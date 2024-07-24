from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from app.routers.router_template import router
from app.models.app_model import Base
from app.db.database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JSON to Pydantic Generator",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    raise HTTPException(status_code=400, detail=exc.errors()[0]['msg'])


app.include_router(router)
# app.include_router(user_router.router)
