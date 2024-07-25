import enum
import uuid
from typing import Any, NewType, cast

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeEngine

from app.db.database import Base

# to resolve type conflicts with UUID
Id = NewType("Id", uuid.UUID)
PSQLId = cast(TypeEngine[Id], PG_UUID)


class StateEnum(enum.Enum):
    NEW = 'NEW'
    INSTALLING = 'INSTALLING'
    RUNNING = 'RUNNING'


class App(Base):
    __tablename__ = 'apps'

    uuid: Column[Id] = Column(PSQLId, primary_key=True, default=uuid.uuid4)
    kind: Column[str] = Column(String(32), nullable=False)
    name: Column[str] = Column(String(128), nullable=False)
    version: Column[str] = Column(String(255), nullable=False)
    description: Column[str] = Column(String(4096), nullable=False)
    state: StateEnum = Column(Enum(StateEnum, name='state_enum', nullable=False))  # type: ignore # noqa
    json: Column[Any] = Column(JSONB, nullable=False)

    def __repr__(self):
        return (
            f"App({self.uuid}, {self.kind}, {self.name}, {self.version}, {self.description}, {self.state}, {self.json})"
        )
