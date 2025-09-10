from typing_extensions import TypedDict
from typing import Union
from pydantic import BaseModel
from schema.agent import GraphOutput, GraphInput, ParsedContent


class State(BaseModel):
    """State of the workflow."""

    # Input from the user
    # user_input: str
    inputs: Union[list[GraphInput], None] = None

    parsed_contents: Union[list[ParsedContent], None] = None

    # Output
    results: Union[list[GraphOutput], None] = None

    errors: Union[list[GraphInput], None] = None
    # feedback: str = None
