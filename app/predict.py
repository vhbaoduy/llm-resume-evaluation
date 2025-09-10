import workflow.workflow as workflow
import os
import pandas as pd
import json
from schema.agent import ParsedContent, ParsedJDContent, ParsedResumeContent


OUTPUT_PATH = "outputs/collector"
os.makedirs(OUTPUT_PATH, exist_ok=True)
file_path = "scores.jsonl"
error_file = "score_errors.jsonl"

f = open(f"{OUTPUT_PATH}/{file_path}", "a")
f_error = open(f"{OUTPUT_PATH}/{error_file}", "a")

PARSED_CONTENTS = json.load(
    open(
        "/home/vhbduy/msc/llm-resume-evaluation/outputs/collector/parsed_contents.json",
        "r",
    )
)

graph = workflow.build_graph()
llm_graph = graph.compile()

from IPython.display import Image, display

dot_string = llm_graph.get_graph().draw_mermaid_png(output_file_path="graph.png")

def batch_generator(df, batch_size):
    """
    A generator that yields batches from a pandas DataFrame.
    """
    num_batches = len(df) // batch_size
    for i in range(num_batches):
        start_index = i * batch_size
        end_index = start_index + batch_size
        yield df.iloc[start_index:end_index].to_dict(orient="records")

    # Yield the last remaining batch if it exists
    if len(df) % batch_size != 0:
        yield df.iloc[num_batches * batch_size :].to_dict(orient="records")


def infer_batch(batch):
    states = []
    row_ids = []
    for row in batch:
        states.append(
            {
                "parsed_contents": [
                    {
                        "id": row["_id"],
                        "resume": PARSED_CONTENTS[row["CV"]],
                        "job_description": PARSED_CONTENTS[row["JD"]],
                    }
                ]
            }
        )
        row_ids.append(row["_id"])
    try:
        outputs = llm_graph.batch(inputs=states)
        for output in outputs:
            for result in output["results"]:
                json_line = json.dumps(result)
                # Write the JSON string followed by a newline
                f.write(json_line + "\n")

    except:
        print(f"Error {row_ids}")
        f_error.writelines(row_ids)


DATA_PATH = "data/dataset"
# df = pd.read_csv("data/dataset/meta.csv")
df = pd.read_csv("outputs/collector/error.csv")
batches = list(batch_generator(df, batch_size=1))
# for batch in batches:
#     infer_batch(batch)

# output = llm_graph.abatch(
#     {
#         "inputs": [
#             {
#                 "id": "test",
#                 "job_description": open(
#                     "/home/vhbduy/msc/llm-resume-evaluation/data/sample/jd_senior.txt",
#                     "r",
#                 ).read(),
#                 "resume": open(
#                     "/home/vhbduy/msc/llm-resume-evaluation/data/sample/cv.txt", "r"
#                 ).read(),
#             }
#         ]
#     }
# )
# print(output)
