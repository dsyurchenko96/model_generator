import enum
import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.database import Base


class StateEnum(enum.Enum):
    NEW = 'NEW'
    INSTALLING = 'INSTALLING'
    RUNNING = 'RUNNING'


class App(Base):
    __tablename__ = 'apps'

    uuid = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kind = Column(String(32), nullable=False)
    name = Column(String(128), nullable=False)
    version = Column(String(255), nullable=False)
    description = Column(String(4096), nullable=False)
    state = Column(Enum(StateEnum, name='state_enum'))
    json = Column(JSONB, nullable=False)

    def __repr__(self):
        return (
            f"App({self.uuid}, {self.kind}, {self.name}, {self.version}, {self.description}, {self.state}, {self.json})"
        )
