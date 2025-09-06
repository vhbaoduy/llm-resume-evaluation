from typing_extensions import TypedDict


class State(TypedDict):
    """State of the workflow."""

    # Input from the user
    # user_input: str
    job_description: str = None
    resume: str = None

    # Immediately
    parsed_jd: str = None
    parsed_resume: str = None

    # Output
    reasoning: str = None
    score: float = None
    # feedback: str = None
