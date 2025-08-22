from langgraph.graph import StateGraph, START, END
from app.agents.sentence_classification import SentenceClassificationAgent
from app.workflow.state import State




def build_graph():
    """Build the workflow graph."""
    graph = StateGraph(state_schema=State)

    # Define the nodes
    # graph.add_node(START, load_job_description)
    # graph.add_node("load_resume", load_resume)
    # graph.add_node("evaluate_resume", evaluate_resume)
    # graph.add_node("provide_feedback", provide_feedback)
    # graph.add_node(END)

    # # Define the edges
    # graph.add_edge(START, "load_resume")
    # graph.add_edge("load_resume", "evaluate_resume")
    # graph.add_edge("evaluate_resume", "provide_feedback")
    # graph.add_edge("provide_feedback", END)

    return graph