from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser

import sys

sys.path.append(".")  # Adjust the path as necessary to import from app.agents
from app.agents.base import BaseAgent
import app.agents.utils as utils


class SentenceClassificationAgent(BaseAgent):
    _NAME = "sentence_classification"

    def __init__(self, llm: BaseChatModel):
        super().__init__(name=self._NAME, llm=llm)
        self.model = llm
        self.prompt = """
You are a sentence classifier in Resume Scaning.  Read the following text review and classify its as (Experience, Education, Skill, Project, PersonalInFormation, Others). Provide ONLY one label.

Here are a few examples:

Sentence: Deployed the applications on Web Logic Application Server.
Classification: Experience

Sentence: 	Used Java Messaging Services (JMS) and Backend messaging for reliable and asynchronous exchange of important information such as payment status report.
Classification: Experience

Sentence: Achyuth 540-999-8048 achyuth.java88@gmail.com
Classification: PersonalInFormation

Sentence: DWH technologies: OLAP. RDBMS: SQL Server 2000/2005/2008 R2, Oracle 8, 9i, 10g, Sybase IQ. Development/Productivity Tools: Adobe Acrobat, MS Office, ODBC, Visual Basic
Classication: Skill

Help me respond with the json format with KEY as label and VALUE as list of sentences that match the label.
{{
    "Experience": [
        "Deployed the applications on Web Logic Application Server.",
        "Used Java Messaging Services (JMS) and Backend messaging for reliable and asynchronous exchange of important information such as payment status report."
    ],
    ...
}}

Content: {content}
Reponse: 
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

    def __call__(self, content: str) -> dict:
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
