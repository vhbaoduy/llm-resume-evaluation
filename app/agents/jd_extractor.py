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
You are an expert at extracting key information from job descriptions. Your task is to meticulously analyze the provided job description and extract all relevant details, categorizing them under the following specific categories: Experience, Education, Skill, CompanyInfo, OtherRequirement, and OtherInfomation.

Here's how to approach the task:

1.  **Read the job description carefully.** Comprehend all requirements, responsibilities, and contextual information.
2.  **Identify and extract key phrases and sentences** that precisely fit each category.
    *   **Experience:** Focus on the required or preferred years of experience, specific prior job titles, industry exposure, and types of professional tasks or environments sought (e.g., "5+ years of experience in software development," "Proven track record in managing cross-functional teams," "Experience with Agile methodologies").
    *   **Education:** Extract all required or preferred educational qualifications, degrees, certifications, and fields of study (e.g., "Bachelor's degree in Computer Science or a related field," "Master's degree preferred," "AWS Certified Developer certification").
    *   **Skill:** Identify both technical (hard) and interpersonal (soft) skills explicitly mentioned as necessary or beneficial (e.g., "Proficiency in Python, Java, and SQL," "Strong communication and collaboration skills," "Experience with data analysis tools like Tableau," "Problem-solving abilities").
    *   **CompanyInfo:** Extract details about the hiring company itself, its mission, values, culture, industry, size, team structure, or general description (e.g., "Join a fast-paced startup environment," "Our mission is to revolutionize healthcare," "Collaborative and inclusive culture," "Leader in AI-driven solutions").
    *   **OtherRequirement:** Capture any explicit, non-negotiable requirements that don't fit into Experience, Education, or Skill, such as legal eligibility, specific work conditions, travel expectations, security clearances, or specific soft skills framed as mandatory requirements.
    *   **OtherInfomation:** Include any remaining important contextual information, benefits, perks, application process details, EEO statements, or any other descriptive text that provides additional context but isn't a direct requirement (e.g., "Competitive salary and benefits package," "Opportunity for professional growth," "We are an equal opportunity employer," "Flexible work arrangements").

3.  **Output the extracted information** in a JSON format, strictly adhering to the schema below. Each category should contain a list of strings. If a category has no relevant information, the list *must* be empty (`[]`). Do not use `null` for empty lists.

**Data Input:**

You will receive a dictionary with two keys: "id" and "value". The "id" is a unique identifier for the job description, and the "value" contains the job description text.

**Output Format:**

Return a dictionary where the key is the "id" from the input and the value is a dictionary representing the parsed content.
```json
{{
    "xxx": {{
        "Experience": ["list of experience-related strings"],
        "Education": ["list of education-related strings"],
        "Skill": ["list of skill-related strings"],
        "CompanyInfo": ["list of company information strings"],
        "OtherRequirement": ["list of other requirement strings"],
        "OtherInfomation": ["list of other general information strings"]
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
