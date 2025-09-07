from pydantic import BaseModel
from typing import Union


class ParsedContent(BaseModel):
    Experience: list[str]
    Education: list[str]
    Skill: list[str]
    Project: list[str]
    PersonalInformation: Union[list[str], None] = None
    Others: Union[list[str], None] = None


class DataInput(BaseModel):
    id: str
    value: str
