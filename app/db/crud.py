import json
from typing import Type

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.app_model import App, Id, StateEnum
from app.models.main_model import Configuration


def read_document(db: Session, uuid: Id):
    response = db.query(App).filter_by(uuid=uuid).first()
    if response is None:
        return None
    return response


def create_document(db: Session, document: App):
    response = db.query(App).filter_by(uuid=document.uuid).first()
    if response is not None:
        return None
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update_document_state(db: Session, uuid: Id, state: StateEnum):
    response = db.query(App).filter_by(uuid=uuid).first()
    if response is None:
        return None
    response.state = state
    db.merge(response)
    db.commit()
    db.refresh(response)
    return response


def update_document_configuration(db: Session, uuid: Id, configuration: Configuration):
    response = db.query(App).filter_by(uuid=uuid).first()
    if response is None:
        return None
    json_str = str(response.json)
    dic = json.loads(json_str)
    dic["configuration"] = configuration.__dict__
    json_dict = jsonable_encoder(dic)
    response.json = json.dumps(json_dict)  # type: ignore
    db.merge(response)
    db.commit()
    db.refresh(response)
    return response


def update_document_settings(db: Session, uuid: Id, settings: dict):
    response = db.query(App).filter_by(uuid=uuid).first()
    if response is None:
        return None
    json_str = str(response.json)
    json_dict = json.loads(json_str)
    json_dict["configuration"]["settings"] = settings
    response.json = json.dumps(json_dict)  # type: ignore
    db.merge(response)
    db.commit()
    db.refresh(response)
    return response


def delete_document(db: Session, uuid: Id) -> Type[App] | None:
    response = db.query(App).filter_by(uuid=uuid).first()
    if response is None:
        return None
    db.delete(response)
    db.commit()
    return response
