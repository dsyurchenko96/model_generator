from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError

from app.routers.router_template import router

app = FastAPI(
    title="JSON to Pydantic Generator",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    raise HTTPException(status_code=400, detail="Validation Error")


app.include_router(router)
# app.include_router(user_router.router)
