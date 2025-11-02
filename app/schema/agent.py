from pydantic import BaseModel
from typing import Union


class GraphInput(BaseModel):
    id: Union[str, None] = None
    resume: str
    job_description: str


class ParsedJDContent(BaseModel):
    Experience: list[str]
    Education: list[str]
    Skill: list[str]
    CompanyInfo: Union[list[str], None] = None
    OtherRequirement: Union[list[str], None] = None
    OtherInfomation: Union[list[str], None] = None


class ParsedResumeContent(BaseModel):
    Experience: list[str]
    Education: list[str]
    Skill: list[str]
    Project: list[str]
    PersonalInformation: Union[list[str], None] = None
    Others: Union[list[str], None] = None


class ParsedContent(BaseModel):
    id: Union[str, int]
    resume: Union[str, dict, ParsedResumeContent]
    job_description: Union[str, dict, ParsedJDContent]


class GraphOutput(BaseModel):
    id: Union[str, None] = None
    score: float
    reasoning: str


class DataInput(BaseModel):
    id: str
    value: str
