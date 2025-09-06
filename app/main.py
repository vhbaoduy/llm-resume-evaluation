from workflow.workflow import build_graph, initialize_state
from fastapi import FastAPI
from schema.user_input import UserInput
from langgraph.checkpoint.memory import InMemorySaver

from fastapi.responses import StreamingResponse
import json

import logging

# logging

MEMORY = InMemorySaver()

app = FastAPI()


@app.post("/evaluate")
def evaluate(user_input: UserInput):
    jd = user_input.job_description
    resume = user_input.resume

    graph = build_graph()

    app = graph.compile(checkpointer=None)

    state = initialize_state(job_description=jd, resume=resume)

    resp = app.invoke(state)
    return resp

    # def _produce_content():
    #     for event in app.stream(state):
    #         event_str = json.dumps(event)
    #         yield event_str + "\n"

    # return StreamingResponse(_produce_content(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
