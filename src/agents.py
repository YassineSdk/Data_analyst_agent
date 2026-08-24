from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from models import *
from utils import load_yaml


# initiating the llm object
llm = init_chat_model(
    model="model",
    model_provider="groq",
    temperature=0
)


def llm_prompt(filename:str):
    prompt = ChatPromptTemplate.from_messages([
        ("system",load_yaml(filename)),
        ("human",human_template)
    ])

    return prompt

# defining the prompt
sql_generator_prompt  = llm_prompt("dev_prompt.yaml")
sql_auditor_prompt = llm_prompt("audit_prompt.yaml")
result_analyst_prompt = llm_prompt("analyst_prompt.yaml")

# llm objects
sql_generator_llm  = sql_generator_prompt | llm.with_structured_output(SQLState)
sql_auditor_llm  = sql_auditor_prompt | llm.with_structured_output(AuditState)
result_analyst_llm = result_analyst_prompt | llm.with_structured_output(ResponseState)
