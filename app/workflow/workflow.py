import uuid
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from agents.sentence_classification import SentenceClassificationAgent
from workflow.state import State

from agents.evaluation import EvalutionAgent
from agents.content_parser import ContentAnalyzer

model = init_chat_model(
    model="gemma-3n-e2b-it", model_provider="google_genai", temperature=0
)
SENTENCE_CLASSIFICATION_AGENT = SentenceClassificationAgent(llm=model)
# CONTENT_ANALYZER_AGENT = ContentAnalyzer(llm=model)
EVALUATION_AGENT = EvalutionAgent(llm=model)


def validate_input(state: State):
    print("Validate input")
    return state


def parse_content(state: State):
    jd = state["job_description"]
    resume = state["resume"]

    jd_content = SENTENCE_CLASSIFICATION_AGENT(content=jd)
    resume_content = SENTENCE_CLASSIFICATION_AGENT(content=resume)

    return {"parsed_jd": jd_content, "parsed_resume": resume_content}


def evaluate_pair_matching(state: State):
    data_id = str(uuid.uuid4())
    outputs = EVALUATION_AGENT(
        data=[
            {
                "data_id": data_id,
                "job_description": state["parsed_jd"],
                "resume": state["parsed_resume"],
            }
        ]
    )
    # print(outputs)
    if len(outputs) == 0:
        return state
    result = outputs[0]
    if result["data_id"] == data_id:
        result.pop("data_id")
        return {"score": result["score"], "reasoning": result["reasoning"]}


def build_graph():
    """Build the workflow graph."""
    graph = StateGraph(state_schema=State)

    # Define the nodes
    graph.add_node("validate_input", validate_input)
    graph.add_node("parse_content", parse_content)
    graph.add_node("evaluate", evaluate_pair_matching)

    graph.add_edge(START, "validate_input")
    graph.add_edge("validate_input", "parse_content")
    graph.add_edge("parse_content", "evaluate")
    graph.add_edge("evaluate", END)

    return graph


def initialize_state(job_description: str, resume: str):
    return State(job_description=job_description, resume=resume)
