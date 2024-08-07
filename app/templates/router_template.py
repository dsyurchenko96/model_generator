from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db
from app.models.app_model import App, Id, StateEnum
from app.models.main_model import Configuration, MainModel

router = APIRouter(
    prefix="/test",
    responses={
        "400": {"description": "Bad Request"},
        "404": {"description": "Not Found"},
        "409": {"description": "Conflict"},
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
        json=document.json(),
    )
    response = crud.create_document(db, app)
    if response is None:
        raise HTTPException(status_code=409, detail="Document already exists")
    return doc_id


@router.delete(
    "/{uuid}/",
    status_code=204,
    response_model=None,
    responses={"204": {"description": "Document deleted successfully"}},
)
def delete_document(uuid: Id, db: Session = Depends(get_db)) -> None:
    response = crud.delete_document(db, uuid)
    if response is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return None


@router.get("/{uuid}/", status_code=200)
def get_document(uuid: Id, db: Session = Depends(get_db)):
    response = crud.read_document(db, uuid)
    if response is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return response


@router.get("/{uuid}/state/", status_code=200)
def get_document_state(uuid: Id, db: Session = Depends(get_db)):
    response = crud.read_document(db, uuid)
    if response is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return response.state


@router.put("/{uuid}/state/", status_code=200)
def put_document_state(uuid: Id, state: StateEnum, db: Session = Depends(get_db)):
    response = crud.update_document_state(db, uuid, state)
    if response is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return response


@router.put("/{uuid}/configuration/", status_code=200)
def put_document_config(uuid: Id, config: Configuration, db: Session = Depends(get_db)):
    response = crud.update_document_configuration(db, uuid, config)
    if response is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return response


@router.put("/{uuid}/settings/", status_code=200)
def put_document_settings(uuid: Id, settings: dict, db: Session = Depends(get_db)):
    response = crud.update_document_settings(db, uuid, settings)
    if response is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return response
