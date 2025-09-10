import uuid
import os
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from langchain.chat_models import init_chat_model
from agents.resume_extractor import ResumeExtractor
from agents.evaluation import EvaluationAgent
from agents.jd_extractor import JDExtractor

model = init_chat_model(
    model="gemma-3n-e2b-it", model_provider="google_genai", temperature=0
)
RESUME_EXTRACTOR = ResumeExtractor(llm=model)
JD_EXTRACTOR = JDExtractor(llm=model)
EVALUATION_AGENT = EvaluationAgent(llm=model)


def prepare_data_for_sentence_classification(
    resume: str, job_description: str, id: str = None
):
    if id is None:
        id = str(uuid.uuid4())
    return [
        {"id": f"resume_{id}", "value": resume},
        {"id": f"jd_{id}", "value": job_description},
    ]


def prepare_data_for_evaluation(resume: str, job_description: str, id: str = None):
    if id is None:
        id = str(uuid.uuid4())

    return {"data_id": id, "resume": resume, "job_description": job_description}


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


OUTPUT_PATH = "outputs/collector"
os.makedirs(OUTPUT_PATH, exist_ok=True)
file_path = "outputs.jsonl"
error_file = "errors.jsonl"

DATA_PATH = "data/dataset"
df = pd.read_csv("data/dataset/meta.csv")


# batches = list(batch_generator(df, batch_size=1))
unique_resumes = df["CV"].unique()
unique_jds = df["JD"].unique()
print(len(unique_resumes), len(unique_jds))


def process_resumes(resumes: list[str]):
    f = open(f"{OUTPUT_PATH}/{file_path}", "a")
    f_error = open(f"{OUTPUT_PATH}/{error_file}", "a")
    for resume_id in resumes:
        resume = open(
            os.path.join(
                DATA_PATH,
                "CV",
                resume_id + ".txt",
            ),
            "r",
        ).read()
        try:
            extracted_resume = RESUME_EXTRACTOR(
                content=[{"id": resume_id, "value": resume}]
            )
            # Convert each dictionary to a JSON string
            json_line = json.dumps(extracted_resume)
            # Write the JSON string followed by a newline
            f.write(json_line + "\n")
            print(f"ERROR {resume_id}")
        except:
            f_error.write(resume_id + "\n")


def process_jds(job_descriptions):
    f = open(f"{OUTPUT_PATH}/{file_path}", "a")
    f_error = open(f"{OUTPUT_PATH}/{error_file}", "a")
    for jd_id in job_descriptions:
        jd = open(
            os.path.join(
                DATA_PATH,
                "JD",
                jd_id + ".txt",
            ),
            "r",
        ).read()

        try:
            extracted_resume = JD_EXTRACTOR(content=[{"id": jd_id, "value": jd}])
            # Convert each dictionary to a JSON string
            json_line = json.dumps(extracted_resume)
            # Write the JSON string followed by a newline
            f.write(json_line + "\n")
        except:
            f_error.write(jd_id + "\n")
            print(f"ERROR {jd_id}")


import threading

threads = [
    threading.Thread(target=func, args=(arg,))
    for func, arg in [(process_resumes, unique_resumes), (process_jds, unique_jds)]
]
[
    thread.start() for thread in threads
]
[
    thread.join() for thread in threads
]

# def process_batch(batch: list[dict]):
#     try:
#         job_descriptions = []
#         resumes = []
#         data_ids = []

#         for row in batch:
#             data_ids.append(row["_id"])
#             resume = open(
#                 os.path.join(
#                     DATA_PATH,
#                     "CV",
#                     row["CV"] + ".txt",
#                 ),
#                 "r",
#             ).read()
#             jd = open(
#                 os.path.join(
#                     DATA_PATH,
#                     "JD",
#                     row["JD"] + ".txt",
#                 ),
#                 "r",
#             ).read()
#             resume, jd = prepare_data_for_sentence_classification(
#                 resume=resume, job_description=jd, id=row["_id"]
#             )
#             resumes.append(resume)
#             job_descriptions.append(jd)

#         parsed_resumes = RESUME_EXTRACTOR(content=resumes)
#         parsed_jds = JD_EXTRACTOR(content=job_descriptions)

#         data_stage2 = []
#         for _id in data_ids:
#             resume_id = f"resume_{_id}"
#             jd_id = f"jd_{_id}"

#             if resume_id not in parsed_resumes or jd_id not in parsed_jds:
#                 # print("Pass {_id}")
#                 print(f"ERROR {_id}")
#                 with open(error_file, "a") as f:
#                     f.write(_id + "\n")
#                 continue

#             parsed_resume = parsed_resumes[resume_id]
#             parsed_jd = parsed_jds[jd_id]
#             data_stage2.append(
#                 {"data_id": _id, "resume": parsed_resume, "job_description": parsed_jd}
#             )

#         result_stage2 = EVALUATION_AGENT(data=data_stage2)
#         with open(file_path, "a") as f:
#             for record in result_stage2:
#                 # Convert each dictionary to a JSON string
#                 json_line = json.dumps(record)
#                 # Write the JSON string followed by a newline
#                 f.write(json_line + "\n")
#         return result_stage2
#     except Exception as e:
#         print(e)
#         return None


# with ThreadPoolExecutor(max_workers=2) as executor:
#     futures = executor.map(process_batch, batches)
#     for future in futures:
#         if future is None:
#             continue

#         ids = [value["data_id"] for value in future]
#         print("Processed ids", ids)

# print("Hello")
