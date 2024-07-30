from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError

from app.db.database import engine
from app.models.app_model import Base
from app.templates.router_template import router as router_template


def include_routers_from_init(fastapi_app: FastAPI):
    try:
        from app import __all__ as routers  # type: ignore

        for router in routers:
            fastapi_app.include_router(router)
            print(f"Included router: {router}")
    except ImportError as e:
        print(f"No routers found in __all__. Generate routers via gen-rest command. Error: {e}")
    except AttributeError:
        print("Error importing routers from __all__. No routers generated.")


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JSON to Pydantic Generator",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    raise HTTPException(status_code=400, detail=exc.errors()[0]["msg"])


include_routers_from_init(app)
app.include_router(router_template)
