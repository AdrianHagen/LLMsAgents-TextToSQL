from langgraph import LangGraph
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv

load_dotenv()


def generate_query_from_state(state: dict) -> str:
    prompt = f"""You are an AI that generates SQL queries based on the given state. The state is as follows:

{state}

Generate a correct SQL query based on the state."""

    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    response = llm.generate(prompt)
    return response["choices"][0]["text"].strip()
