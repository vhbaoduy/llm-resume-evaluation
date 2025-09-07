from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser

import sys

sys.path.append(".")  # Adjust the path as necessary to import from app.agents
from app.agents.base import BaseAgent
import app.agents.utils as utils
import app.schema.agent as schema_agent


class ResumeExtractor(BaseAgent):
    _NAME = "resume_extractor"

    def __init__(self, llm: BaseChatModel):
        super().__init__(name=self._NAME, llm=llm)
        self.model = llm
        self.prompt = """
You are an expert at extracting key information from resumes. Your task is to analyze the provided resume and extract relevant details, categorizing them under the following categories: Experience, Education, Skills, Projects, PersonalInformation and Others.

Here's how to approach the task:

1.  **Read the resume carefully.** Understand the candidate's background and qualifications.
2.  **Identify key phrases and sentences** that fall under each category.
    *   **Experience:**  Focus on job titles, company names, dates of employment, and responsibilities. Extract specific accomplishments and quantifiable results whenever possible (e.g., "Software Engineer at Google, 2018-2023, Developed and maintained key features for the Android operating system, resulting in a 15% increase in user engagement.").
    *   **Education:** Extract the degrees earned, institutions attended, dates of attendance, GPA (if provided), and any relevant honors or awards (e.g., "Bachelor of Science in Computer Science, Stanford University, 2014-2018, GPA: 3.9, Summa Cum Laude").
    *   **Skills:** Identify both hard and soft skills mentioned in the resume. Pay attention to technical skills, programming languages, software proficiency, and interpersonal skills (e.g., "Python, Java, C++, Machine Learning, Data Analysis, Communication, Teamwork, Problem-solving").
    *   **Projects:** Look for descriptions of personal or academic projects, especially those that demonstrate relevant skills and experience (e.g., "Developed a machine learning model to predict customer churn using Python and scikit-learn," "Designed and implemented a web application using React and Node.js").
    *   **PersonalInformation:** Extract information such as name, contact information (phone number, email address, LinkedIn profile), location, and any other personal details provided in the resume (e.g., "John Doe, johndoe@email.com, (123) 456-7890, San Francisco, CA"). Do not include information about race, religion, gender or age.
    *   **Others:** Include any information that doesn't fit into the above categories but is still important, such as awards, certifications, publications, or volunteer experience.

3.  **Output the extracted information** in a JSON format, following the schema below. Each category should contain a list of strings. If a category has no relevant information, the list should be empty or null.

**Data Input:**

You will receive a list of dictionaries, where each dictionary has two keys: "id" and "value". The "id" is a unique identifier for the resume, and the "value" contains the resume text.
{{
    "id": "xxx",
    "value": "Resume Text"
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


# Ensure your API key is set as an environment variable
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
# model = init_chat_model(
#     model="gemma-3n-e2b-it", model_provider="google_genai", temperature=0
# )


# agent = SentenceClassificationAgent(llm=model)
# # Example usage
# content = "Deployed the applications on Web Logic Application Server. Used Java Messaging Services (JMS) and Backend messaging for reliable and asynchronous exchange of important information such as payment status report."
# result = agent(content)
# print(result)  # Should print the classified sentences in JSON format
