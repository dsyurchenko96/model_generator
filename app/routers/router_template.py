from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db
from app.models.app_model import App, StateEnum
from app.utils.main_schema_gen import MainModel

router = APIRouter(
    prefix="/kind",
    responses={
        "400": {"description": "Bad Request"},
        "404": {"description": "Not Found"},
        "500": {"description": "Internal Server Error"},
    },
)


@router.post("/", status_code=201)
def post_document(
    document: MainModel,
    state: StateEnum = StateEnum.NEW,
    db: Session = Depends(get_db),
):
    doc_id = uuid4()
    app = App(
        uuid=doc_id,
        kind=document.kind,
        name=document.name,
        version=document.version,
        description=document.description,
        state=state,
        json=document.dict(),
    )
    response = crud.create_document(db, app)
    if response is None:
        raise HTTPException(status_code=500, detail="Can't create document")
    return doc_id


@router.delete("/{uuid}/", status_code=204, response_model=None,
               responses={"204": {"description": "Document deleted successfully"}})
def delete_document(uuid: UUID, db: Session = Depends(get_db)) -> None:
    response = crud.delete_document(db, uuid)
    if response is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return None
