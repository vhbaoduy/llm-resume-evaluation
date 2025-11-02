import uuid
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from workflow.state import State

from agents.evaluation import EvaluationAgent
from agents.resume_extractor import ResumeExtractor
from agents.jd_extractor import JDExtractor
import workflow.node as node


model = init_chat_model(
    model="gemma-3n-e2b-it", model_provider="google_genai", temperature=0
)
RESUME_EXTRACTOR = ResumeExtractor(llm=model)
EVALUATION_AGENT = EvaluationAgent(llm=model)
JD_EXTRACTOR = JDExtractor(llm=model)

CONFIGS = [
    {"obj": node.ValidateInputNode, "configs": {"name": "VALIDATION_INPUT"}},
    {
        "obj": node.ParseContentNode,
        "configs": {
            "name": "CONTENT_EXTRACTION",
            "jd_extractor": JD_EXTRACTOR,
            "resume_extractor": RESUME_EXTRACTOR,
        },
    },
    {
        "obj": node.EvaluatePairMatchingNode,
        "configs": {"name": "EVALUATION", "evaluation_agent": EVALUATION_AGENT},
    },
]

NODES: list[node.BaseNode] = [value["obj"](**value["configs"]) for value in CONFIGS]


class Router:
    pass
    # @classmethod
    # def


# def initialize_state(job_description: str, resume: str):
#     return State(job_description=job_description, resume=resume)


# def validate_input(state: State):
#     print("Validate input")
#     return state


# def parse_content(state: State):
#     _id = str(uuid.uuid4())
#     jd_id = f"jd_{_id}"
#     resume_id = f"resume_{_id}"

#     jd = state["job_description"]
#     resume = state["resume"]

#     extracted_resume = RESUME_EXTRACTOR(
#         content=[
#             {"id": f"resume_{_id}", "value": resume},
#         ]
#     )
#     extracted_jd = JD_EXTRACTOR(
#         content=[
#             {"id": f"jd_{_id}", "value": jd},
#         ]
#     )
#     parsed_jd = None
#     parsed_resume = None
#     if resume_id in extracted_resume:
#         parsed_resume = extracted_resume[resume_id]

#     if jd_id in extracted_jd:
#         parsed_jd = extracted_jd[jd_id]

#     return {"parsed_jd": parsed_jd, "parsed_resume": parsed_resume}


# def evaluate_pair_matching(state: State):
#     data_id = str(uuid.uuid4())
#     outputs = EVALUATION_AGENT(
#         data=[
#             {
#                 "id": data_id,
#                 "job_description": state["parsed_jd"],
#                 "resume": state["parsed_resume"],
#             }
#         ]
#     )
#     # print(outputs)
#     if len(outputs) == 0:
#         return state
#     result = outputs[0]
#     if result["id"] == data_id:
#         result.pop("id")
#         return {"score": result["score"], "reasoning": result["reasoning"]}


def build_graph():
    """Build the workflow graph."""
    graph = StateGraph(state_schema=State)

    # Define the nodes
    # graph.add_node("validate_input", validate_input)
    # graph.add_node("parse_content", parse_content)
    # graph.add_node("evaluate", evaluate_pair_matching)

    # graph.add_edge(START, "validate_input")
    # graph.add_edge("validate_input", "parse_content")
    # graph.add_edge("parse_content", "evaluate")
    # graph.add_edge("evaluate", END)
    for user_node in NODES:
        graph.add_node(user_node.name, user_node)

    graph.add_edge(START, "VALIDATION_INPUT")
    graph.add_edge("VALIDATION_INPUT", "CONTENT_EXTRACTION")
    graph.add_edge("CONTENT_EXTRACTION", "EVALUATION")
    graph.add_edge("EVALUATION", END)

    return graph
