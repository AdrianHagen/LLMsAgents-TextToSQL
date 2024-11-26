from langchain_openai import OpenAI
import os


def generate_sql_query_creator(state: dict) -> str:
    prompt = f"""You are an AI that generates SQL queries based on natural language prompts.
    The natural language prompt is: {state["original_question"]}
    You can use the following tables: {state["relevant_tables"]}

    Generate a correct SQL query based on this information."""

    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = llm.invoke(prompt)
    state["sql_query"] = response
    return state
