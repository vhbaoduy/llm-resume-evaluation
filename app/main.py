from workflow.workflow import build_graph
from fastapi import FastAPI
from schema.user_input import UserInput
from schema.file import FileRequest
from langgraph.checkpoint.memory import InMemorySaver

from fastapi.responses import StreamingResponse
import json

import logging
from controllers.file import FileController
from controllers.matching import MatchingController
from fastapi.middleware.cors import CORSMiddleware


# logging

MEMORY = InMemorySaver()

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Set to True if your frontend sends cookies or authorization headers
    allow_methods=["*"],  # Or specify specific methods like ["GET", "POST"]
    allow_headers=["*"],  # Or specify specific headers
)


@app.post("/extract")
def extract_document(request: FileRequest):
    return FileController.extract_text(request)


@app.post("/evaluate")
def evaluate(user_input: UserInput):
    # jd = user_input.job_description
    # resume = user_input.resume

    # graph = build_graph()

    # app = graph.compile(checkpointer=None)

    # state = initialize_state(job_description=jd, resume=resume)

    # resp = app.invoke(state)
    # resp = {}
    result = MatchingController.matching(user_input)
    result["score"] = result["score"] * 10
    return result

    # def _produce_content():
    #     for event in app.stream(state):
    #         event_str = json.dumps(event)
    #         yield event_str + "\n"

    # return StreamingResponse(_produce_content(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
