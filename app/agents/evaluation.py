from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser

import sys

sys.path.append(".")  # Adjust the path as necessary to import from app.agents
sys.path.append("..")  # Adjust the path as necessary to import from app.agents

from app.agents.base import BaseAgent
import app.agents.utils as utils


class EvalutionAgent(BaseAgent):
    def __init__(self, llm: BaseChatModel):
        self.model = llm
        self.prompt = """
You are an expert in evaluating job applications and assessing candidate suitability. Your task is to analyze a Job Description (JD) and a Resume and assign a match score (0-10) reflecting the degree of compatibility. Provide a detailed justification for the score, explaining the reasoning behind your assessment. The output should be a JSON formatted list containing the score and the corresponding reasoning.

**Instructions:**

1. **Analyze the Job Description (JD) and Resume:** Carefully read both documents to understand the requirements of the job and the candidate's qualifications.
2. **Calculate the Match Score:** Assign a score between 0 and 10, where:
    * **0-2:** Poor or irrelevant resume.
    * **3-4:** Weak match.
    * **5-6:**  Moderate match. 
    * **7-8:**  Good match, minor skill differences. 
    * **9-10:** Strong skill match, very relevant resume. 
3. **Provide a Detailed Justification:** Explain *why* you assigned the score. Specifically, consider the following:
    * **Matching Skills:** List the skills from the JD that the resume demonstrates.
    * **Relevant Experience:** List the relevant experience from the resume that aligns with the JD.
    * **Gaps in Qualifications:** Identify any skills or experience from the JD that are *not* present in the resume.
    * **Experience Level:** Assess whether the candidate's experience level aligns with the requirements of the job.
    * **Keywords:** Note any keywords from the JD that are present or absent in the resume.
    * **Overall Fit:** Provide a holistic assessment of how well the candidate's profile aligns with the overall requirements of the role.
4. **Maintain a Professional and Objective Tone:** Avoid subjective opinions or personal biases. Focus on factual evidence from the JD and Resume.

**Input:**

{data}

INPUT DESCRIPTION:
[
    {{
        "data_id" (string): The ID of data,
        "job_description" (string or dict):  All sentences in a job description
        "resume" (string or dict): All sentences in a resume.
    }}
]

**Output:**
List of JSON objects in the following format corresponding to each JD and Resume pair:
[
  {{
    "data_id": The ID of input data,
    "score": [Your Calculated Score Here],
    "reasoning": "[Your Detailed Justification Here]"
  }}
] 

YOUR RESPONSE MUST BE IN JSON FORMAT AS SPECIFIED ABOVE. DO NOT INCLUDE ANY ADDITIONAL TEXT OR EXPLANATIONS OUTSIDE THE JSON STRUCTURE.
"""
        self.chain = (
            PromptTemplate(
                input_variables=["job_descriptions", "resumes"],
                template=self.prompt,
            )
            | self.model
            | StrOutputParser()
            | utils.extract_json_from_string
        )

    def __call__(self, data: list[dict]) -> list[dict]:
        """
        Evaluate the job descriptions and resumes, returning a structured response.

        Args:
            job_descriptions: The job descriptions to evaluate.
            resumes: The resumes to evaluate.

        Returns:
            dict: A structured response containing evaluation results.
        """
        return self.chain.invoke(
            {
                "data": data,
            }
        )


# import pandas as pd
# import time
# import tqdm
# import json
# import os
# import concurrent.futures


# def batch_generator(df, batch_size):
#     """
#     A generator that yields batches from a pandas DataFrame.
#     """
#     num_batches = len(df) // batch_size
#     for i in range(num_batches):
#         start_index = i * batch_size
#         end_index = start_index + batch_size
#         yield df.iloc[start_index:end_index].to_dict(orient="records")

#     # Yield the last remaining batch if it exists
#     if len(df) % batch_size != 0:
#         yield df.iloc[num_batches * batch_size :].to_dict(orient="records")


# file_path = "outputs.jsonl"
# error_file = "errors.jsonl"
# # open(file_path,"w")
# # open(error_file,"w")


# def evaluate(data: list[dict]):
#     try:
#         model = init_chat_model(
#             model="gemma-3n-e2b-it", model_provider="google_genai", temperature=0
#         )
#         # model = init_chat_model(
#         #     model="llama3.2:1b", model_provider="ollama", temperature=0
#         # )
#         agent = EvalutionAgent(llm=model)
#         result = agent(data)
#         with open(file_path, "a") as f:
#             for record in result:
#                 # Convert each dictionary to a JSON string
#                 json_line = json.dumps(record)
#                 # Write the JSON string followed by a newline
#                 f.write(json_line + "\n")
#         return True
#     except:
#         print(f"ERROR {data}")
#         with open(error_file, "a") as f:
#             for record in data:
#                 # Convert each dictionary to a JSON string
#                 json_line = json.dumps(record)
#                 # Write the JSON string followed by a newline
#                 f.write(json_line + "\n")
#         return False


# # Example usage
# df_train = pd.read_csv("data/train_unpredicted.csv")
# df_train = df_train[["data_id", "job_description", "resume"]]
# batch_size = 6
# responses = []
# batches = list(batch_generator(df_train, batch_size))
# with concurrent.futures.ThreadPoolExecutor(max_workers=3) as excutor:
#     future = excutor.map(evaluate, batches)
#     for result in tqdm.tqdm(future):
#         pass


# print(responses)
# # json.dump(responses, open("data/predictions_gemma3n.json", "w"), indent=4)

# # print(result)  # Should print the classified sentences in JSON format
