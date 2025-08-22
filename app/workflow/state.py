from typing_extensions import TypedDict


class State(TypedDict):
    """State of the workflow."""
    job_description: str
    resume: str
    evaluation: str
    score: float
    feedback: str