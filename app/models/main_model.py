from typing import TypedDict

from pydantic import BaseModel, Field

semver_regex = (
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|["
    r"1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+("
    r"?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


class SchemaConfigField(TypedDict):
    specification: dict
    settings: dict


class MainModel(BaseModel):
    class Config:
        title = "Main Schema"
        extra = "forbid"

    kind: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=4096)
    version: str = Field(regex=semver_regex)
    configuration: SchemaConfigField

    def __repr__(self):
        return f"MainModel({self.kind}, {self.name}, {self.version}, {self.description}, {self.configuration})"
