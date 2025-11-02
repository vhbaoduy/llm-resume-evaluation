from schema.user_input import UserInput
from schema.agent import GraphInput, GraphOutput
import workflow.workflow as workflow
from workflow.state import State

REQUEST_ID = 0


class MatchingController:
    @staticmethod
    def matching(
        request: UserInput,
        method: str = None,
    ):
        global REQUEST_ID
        graph = workflow.build_graph()
        llm_graph = graph.compile()
        state = State(
            inputs=[
                GraphInput(
                    id=f"request_{REQUEST_ID}",
                    resume=request.resume,
                    job_description=request.job_description,
                )
            ]
        )
        output = llm_graph.invoke(state)
        result: GraphOutput = None
        if len(output["results"]) > 0:
            result = output["results"][0]
            REQUEST_ID += 1

        return result
