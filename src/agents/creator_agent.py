from langchain_openai import OpenAI
import os
import prompt_templates.creator_agent as creator_agent_templates
from langchain.prompts import PromptTemplate
import json
from state_types import State


def create_sql_query_creator(state: State) -> str:
    feedback = ""
    errors = ""
    if len(state["feedbacks"]) > 0:
        feedback = json.dumps(state["feedbacks"])
    if len(state["errors"]) > 0:
        errors = ", ".join(state["errors"])

    prompt = PromptTemplate.from_template(creator_agent_templates.TWO_SHOT)
    prompt = prompt.invoke(
        {
            "original_question": state["original_question"],
            "relevant_tables": json.dumps(state["relevant_tables"]),
            "generated_sql_queries": ", ".join(state["generated_sql_queries"]),
            "feedback_trace": feedback,
            "error_trace": errors,
        }
    )
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = llm.invoke(prompt)
    response = response.replace("Output:", "").strip()
    state["generated_sql_queries"].append(response)
    return state
