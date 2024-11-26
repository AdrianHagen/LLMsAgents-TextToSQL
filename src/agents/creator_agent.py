from langchain_openai import OpenAI
import os
import prompt_templates.creator_agent as creator_agent_templates
from langchain.prompts import PromptTemplate
import json


def create_sql_query_creator(state: dict) -> str:
    prompt = PromptTemplate.from_template(creator_agent_templates.TWO_SHOT)
    print(f"Creator agent: relevant tables: {json.dumps(state['relevant_tables'])}")
    prompt = prompt.invoke(
        {
            "original_question": state["original_question"],
            "relevant_tables": ", ".join(state["relevant_tables"]),
            "feedback_trace": json.dumps(state["feedbacks"]),
        }
    )
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = llm.invoke(prompt)
    response = response.replace("Output:", "").strip()
    print(f"Creator agent: Processed response: {response}")
    state["generated_sql_queries"].append(response)
    return state
