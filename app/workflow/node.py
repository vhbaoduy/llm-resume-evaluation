from workflow.state import State
from schema.agent import ParsedContent, GraphInput, GraphOutput
import uuid
from typing import Dict, Any, Callable, Union

from agents.jd_extractor import JDExtractor
from agents.evaluation import EvaluationAgent
from agents.resume_extractor import ResumeExtractor


class BaseNode:
    """
    Base class for all nodes in the pipeline.

    Each node represents a single, distinct step in a workflow.
    It defines a common interface with a `__call__` method that
    takes and returns a 'state' dictionary.
    """

    def __init__(self, name: str):
        self.name = name

    def __call__(self, state: State) -> State:
        """
        The core logic of the node. Must be implemented by subclasses.

        Args:
            state: The current state of the workflow as a dictionary.

        Returns:
            The updated state dictionary after the node's execution.
        """
        raise NotImplementedError("Subclasses must implement the __call__ method.")


class ValidateInputNode(BaseNode):
    """
    A node to validate the initial input data.

    This node ensures that the 'job_description' and 'resume' fields
    are present in the state before proceeding.
    """

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)

    def __call__(self, state: Union[State, dict]) -> State:
        """
        Validates the input state.

        Args:
            state: The workflow state, expected to contain 'job_description'
                   and 'resume' strings.

        Returns:
            The unmodified state if validation passes.
            Raises a ValueError if validation fails.
        """
        print(f"[{self.name}] Validating input...")
        if isinstance(state, dict):
            state = State(**state)
        return state


class ParseContentNode(BaseNode):
    """
    A node to parse and extract structured data from raw content.

    It uses external 'extractor' agents to process the raw job description
    and resume, adding the parsed data to the state.
    """

    def __init__(
        self,
        name: str,
        jd_extractor: JDExtractor,
        resume_extractor: ResumeExtractor,
        **kwargs,
    ):
        super().__init__(name=name)
        self.jd_extractor = jd_extractor
        self.resume_extractor = resume_extractor

    def __call__(self, state: State) -> State:
        if state.parsed_contents is not None:
            return state

        parsed_contents = []
        resume_batches = []
        jd_batches = []
        result_ids = []
        for i, content in enumerate(state.inputs):
            _id = str(i)
            if content.id is not None:
                _id = content.id

            result_ids.append(_id)
            resume_batches.append({"id": _id, "value": content.resume})
            jd_batches.append({"id": _id, "value": content.job_description})

        extracted_resumes = self.resume_extractor(content=resume_batches)
        extracted_jds = self.jd_extractor(content=jd_batches)

        for _id in result_ids:
            if _id not in extracted_resumes or _id not in extracted_jds:
                print(f"Pass id {_id}")
                continue
            parsed_contents.append(
                ParsedContent(
                    id=_id,
                    job_description=extracted_jds.get(_id, ""),
                    resume=extracted_resumes.get(_id, ""),
                )
            )

        state.parsed_contents = parsed_contents
        return state


class EvaluatePairMatchingNode(BaseNode):
    """
    A node to evaluate the match between a parsed job description and a resume.

    It uses an external 'evaluation agent' to calculate a score and reasoning,
    which are then added to the state.
    """

    def __init__(self, name, evaluation_agent: EvaluationAgent, **kwargs):
        super().__init__(name)
        self.evaluation_agent = evaluation_agent

    def __call__(self, state: State) -> State:
        """
        Evaluates the parsed job description and resume.

        Args:
            state: The workflow state containing 'parsed_jd' and 'parsed_resume'.

        Returns:
            The updated state with 'score' and 'reasoning' keys.
        """
        outputs = self.evaluation_agent(
            data=[value.model_dump() for value in state.parsed_contents]
        )
        state.results = outputs
        return state
