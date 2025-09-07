from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser

import sys

sys.path.append(".")  # Adjust the path as necessary to import from app.agents
from app.agents.base import BaseAgent
import app.agents.utils as utils
import app.schema.agent as schema_agent


class JDExtractor(BaseAgent):
    _NAME = "job_description_extractor"

    def __init__(self, llm: BaseChatModel):
        super().__init__(name=self._NAME, llm=llm)
        self.model = llm
        self.prompt = """
You are an expert at extracting key information from job descriptions. Your task is to analyze the provided job description and extract relevant details, categorizing them under the following categories: Experience, Education, Skills, Projects, and Others.

Here's how to approach the task:

1.  **Read the job description carefully.** Understand the requirements and responsibilities outlined.
2.  **Identify key phrases and sentences** that fall under each category.
    *   **Experience:**  Focus on the years of experience required, specific job titles held previously, and the type of experience sought (e.g., "5+ years of experience in software development," "Experience with Agile methodologies").
    *   **Education:** Extract the required or preferred educational qualifications, degrees, certifications, and fields of study (e.g., "Bachelor's degree in Computer Science," "Master's degree in a related field," "AWS Certified Developer").
    *   **Skills:** Identify both hard and soft skills mentioned in the job description (e.g., "Proficiency in Python," "Strong communication skills," "Experience with data analysis," "Project management skills").
    *   **Projects:** Look for mentions of specific projects the candidate might work on or experience with similar projects that are desired (e.g., "Experience in developing cloud-based applications," "Worked on projects involving machine learning," "Experience with large-scale data migration projects").
    *   **Others:** Include any information that doesn't fit into the above categories but is still important, such as information about personal traits, or other requirements. If there is personal information, such as name, age, gender, etc, please put it in PersonalInformation.

3.  **Output the extracted information** in a JSON format, following the schema below. Each category should contain a list of strings. If a category has no relevant information, the list should be empty.

**Data Input:**

You will receive a list of dictionaries, where each dictionary has two keys: "id" and "value". The "id" is a unique identifier for the job description, and the "value" contains the job description text.
{{
    "id": "xxx",
    "value": "Text content"
}}

**Output Format:**

Return a dictionary where the key is the "id" from the input and the value is a ParsedContent object (represented as a dictionary).

```json
{{
    "xxx": {{
        "Experience": ["list of experience-related strings"],
        "Education": ["list of education-related strings"],
        "Skill": ["list of skill-related strings"],
        "Project": ["list of project-related strings"],
        "PersonalInformation": ["list of personal information strings or null"],
        "Others": ["list of other relevant strings or null"]
    }}
}}
```

INPUT: {content}
RESPONSE:
"""
        self.chain = (
            PromptTemplate(
                input_variables=["content"],
                template=self.prompt,
            )
            | self.model
            | StrOutputParser()
            | utils.extract_json_from_string
        )

    def __call__(self, content: list[schema_agent.DataInput]) -> dict:
        """
        Classify the content into predefined categories.

        Args:
            content (str): The text content to classify.

        Returns:
            dict: A dictionary with categories as keys and lists of sentences as values.
        """
        return self.chain.invoke({"content": content})
