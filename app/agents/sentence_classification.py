from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model

import google.generativeai as genai
import os

# Ensure your API key is set as an environment variable
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
model = init_chat_model(
    model="gemma-3n-e2b-it", model_provider="google_genai", temperature=0
)
# model = ChatGoogleGenerativeAI(
#     model_name="gemma-3n-e2b-it",
#     goole_api_key=os.getenv("GOOGLE_API_KEY", None)
# )
print(model)

prompt = """
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

class SentenceClassificationAgent:
    def __init__(self, llm: BaseChatModel):
        self.model = llm
