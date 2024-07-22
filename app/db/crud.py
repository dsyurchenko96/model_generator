from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from app.models.app_model import App


def get_document(db: Session, kind: str, uuid: UUID):
    response = (
        db.query(App)
        .filter(
            App.kind == kind,
            App.uuid == uuid,
        )
        .first()
    )
    if response is None:
        return None
    return App.parse_obj(response)


def create_document(db: Session, document: App):
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def delete_document(db: Session, uuid: UUID):
    response = db.query(App).filter(App.uuid == uuid).first()
    if response is None:
        return None
    db.delete(response)
    db.commit()
