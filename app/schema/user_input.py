from pydantic import BaseModel
from typing import Union


class UserInput(BaseModel):
    job_description: str
    resume: str

    jd_file: Union[str, None] = None
    jd_resume: Union[str, None] = None
