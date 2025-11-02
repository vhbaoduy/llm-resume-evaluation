from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser

import sys

sys.path.append(".")  # Adjust the path as necessary to import from app.agents
sys.path.append("..")  # Adjust the path as necessary to import from app.agents

from app.agents.base import BaseAgent
import app.agents.utils as utils


class EvaluationAgent(BaseAgent):
    def __init__(self, llm: BaseChatModel):
        self.model = llm
        self.prompt = """
You are an expert in evaluating job applications and assessing candidate suitability. Your task is to analyze a Job Description (JD) and a Resume and assign a match score (0-10) reflecting the degree of compatibility. Provide a detailed justification for the score, explaining the reasoning behind your assessment. The output should be a JSON formatted list containing the score and the corresponding reasoning.

**Instructions:**

1. **Analyze the Job Description (JD) and Resume:** Carefully read both documents to understand the requirements of the job and the candidate's qualifications. The JD and Resume are provided in a structured format, with key information already extracted and categorized into "Experience," "Education," "Skill," "Project," "PersonalInformation," and "Others."
2. **Calculate the Match Score:** Assign a score between 0 and 10, based on the following criteria:
    * **0-1:** Very Poor Match. The resume is irrelevant to the job description. Key skills and experience are entirely missing.
    * **2-3:** Poor Match. The resume has minimal relevance to the job description. There are very few matching skills or relevant experience entries.
    * **4-5:** Weak Match. The resume demonstrates some relevant skills or experience, but significant gaps exist in key areas.
    * **6-7:** Moderate Match. The resume demonstrates a reasonable alignment with the job requirements, but there are notable areas for improvement or missing qualifications.
    * **8-9:** Good Match. The resume demonstrates a strong alignment with the job requirements. There may be minor skill differences or slight gaps in experience, but the candidate is generally well-qualified.
    * **10:** Excellent Match. The resume is exceptionally well-suited to the job requirements. The candidate possesses all or nearly all of the desired skills and experience.

3. **Provide a Detailed Justification:** Explain *why* you assigned the score. Your reasoning should be clear, concise, and supported by specific evidence from the provided JD and Resume data. Address the following points:

    * **Skill Match Analysis:**
        *   Identify the skills present in both the JD's "Skill" list and the Resume's "Skill" list.
        *   Quantify the overlap by stating the number of matching skills and the total number of skills listed in the JD (e.g., "The resume matches 3 out of 5 required skills from the JD").
        *   List any critical skills from the JD that are missing from the Resume.
    * **Experience Alignment Analysis:**
        *   Identify experience entries in the Resume's "Experience" list that directly align with the requirements described in the JD's "Experience" list.
        *   Highlight specific job titles, responsibilities, or accomplishments that demonstrate a strong fit.
        *   Note any significant discrepancies in experience level or type.
    * **Education Verification:**
        *   Compare the education listed in the Resume's "Education" list with the requirements in the JD's "Education" list.
        *   State whether the candidate meets the minimum educational requirements and if their education is directly relevant to the role.
    * **Project Evaluation:**
        *   Assess the relevance of projects listed in the Resume's "Project" list to the requirements or desired experience outlined in the JD.
        *   Explain how the projects demonstrate relevant skills or experience. If no projects are listed, state this explicitly.
    * **Overall Assessment:**
        *   Provide a concise summary of the candidate's overall suitability for the role, based on the combined analysis of skills, experience, education, and projects.
        *   Justify the assigned score by referencing the key strengths and weaknesses of the candidate's profile.

4. **Maintain a Professional and Objective Tone:** Avoid subjective opinions or personal biases. Base your assessment solely on the factual information presented in the JD and Resume data. Use precise language and avoid vague or ambiguous statements.

**Input:**
[
    {{
        "id": "123",
        "job_description": {{
            "Experience": ["5+ years of software development experience", "Experience with Agile methodologies"],
            "Education": ["Bachelor's degree in Computer Science"],
            "Skill": ["Python", "Java", "Communication", "Problem-solving"],
            "Project": ["Experience with cloud-based applications"],
            "PersonalInformation": null,
            "Others": []
        }},
        "resume": {{
            "Experience": ["Software Engineer at Google, 2018-2023", "Developed and maintained Android applications"],
            "Education": ["Bachelor of Science in Computer Science, Stanford University"],
            "Skill": ["Java", "Communication", "Teamwork"],
            "Project": ["Developed a mobile application for Android"],
            "PersonalInformation": ["John Doe"],
            "Others": []
        }}
    }}
]

**Output:**

```json
[
  {{
    "id": "123",
    "score": 8,
    "reasoning": "The candidate demonstrates a good match with the job description. Matching Skills: Python, Java, Communication. Relevant Experience: The candidate has 5 years of software development experience at Google, aligning with the requirement of 5+ years. Education Alignment: The candidate holds a BS in Computer Science, fulfilling the education requirement. Gaps in Qualifications: The resume does not explicitly mention experience with Agile methodologies. Overall Fit: The candidate's profile aligns well with the requirements, with a minor gap in Agile experience."
  }}
]
```

Input: {data}
Response: 
"""
        self.chain = (
            PromptTemplate(
                input_variables=["data"],
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


import pandas as pd
import time
import tqdm
import json
import os
import concurrent.futures


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


file_path = "outputs_test.jsonl"
error_file = "errors_test.jsonl"
# open(file_path,"w")
# open(error_file,"w")


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
# df = pd.read_csv("data/test.csv")
# df = df[["data_id", "job_description", "resume"]]
# batch_size = 6
# responses = []
# batches = list(batch_generator(df, batch_size))
# with concurrent.futures.ThreadPoolExecutor(max_workers=3) as excutor:
#     future = excutor.map(evaluate, batches)
#     for result in tqdm.tqdm(future):
#         pass


# print(responses)
# json.dump(responses, open("data/predictions_gemma3n.json", "w"), indent=4)

# print(result)  # Should print the classified sentences in JSON format
