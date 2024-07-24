from app.models.app_model import StateEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from copy import deepcopy

from app.models.app_model import App


def read_document(db: Session, uuid: UUID):
    response = db.query(App).filter(App.uuid == uuid).first()
    if response is None:
        return None
    return response


def create_document(db: Session, document: App):
    response = db.query(App).filter(App.uuid == document.uuid).first()
    if response is not None:
        return None
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def update_document_state(db: Session, uuid: UUID, state: StateEnum):
    response = db.query(App).filter(App.uuid == uuid).first()
    if response is None:
        return None
    response.state = state.name
    db.merge(response)
    db.commit()
    db.refresh(response)
    return response

def update_document_configuration(db: Session, uuid: UUID, configuration):
    response = db.query(App).filter(App.uuid == uuid).first()
    if response is None:
        return None
    # TODO: Validate configuration
    # response.json.configuration = configuration
    print(response)
    db.merge(response)
    db.commit()
    db.refresh(response)
    return response

def delete_document(db: Session, uuid: UUID) -> dict:
    response = db.query(App).filter(App.uuid == uuid).first()
    if response is None:
        return None
    db.delete(response)
    db.commit()
    return response
