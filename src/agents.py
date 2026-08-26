from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from models import *
from utils import load_yaml
from dotenv import load_dotenv, find_dotenv

# initiating the llm object
load_dotenv(find_dotenv(".env"))


llm = init_chat_model(
    "groq:openai/gpt-oss-120b")


def llm_prompt(filename:str,human_template:str):
    prompt = ChatPromptTemplate.from_messages([
        ("system",load_yaml(filename)),
        ("human",human_template)
    ])

    return prompt

# defining the prompt
intent_prompt = llm_prompt("intent_prompt.yaml","{human_template}")
sql_generator_prompt  = llm_prompt("dev_prompt.yaml","{human_template}")
sql_auditor_prompt = llm_prompt("audit_prompt.yaml","{human_template}")
result_analyst_prompt = llm_prompt("analyst_prompt.yaml","{human_template}")

# llm objects
intent_analyst_llm = intent_prompt | llm.with_structured_output(IntentState)
sql_generator_llm  = sql_generator_prompt | llm.with_structured_output(SQLState)
sql_auditor_llm  = sql_auditor_prompt | llm.with_structured_output(AuditState)
result_analyst_llm = result_analyst_prompt | llm.with_structured_output(Response)



human_template="""
When appropriate:
- highlight the most important findings
- provide rankings or comparisons
- mention relevant values
- identify patterns directly visible in the results
"""
print(llm_prompt("intent_prompt.yaml",human_template))