from typing import Annotated, List

from typing_extensions import TypedDict

from agents.types import State
from langgraph.graph import StateGraph, START, END
from langchain_openai import OpenAI
import os
import pandas as pd
import json
import sqlfluff


graph_builder = StateGraph(State)

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def retrieve_database_names():
    for _, dirs, _ in os.walk("data/dev/dev_databases"):
        return ", ".join(dirs)


def retrieve_table_names(database_name: str):
    table_names = []
    tables_path = os.path.join("data/dev/dev_databases", database_name)
    for _, dirs, _ in os.walk(tables_path):
        table_names = dirs
    return table_names


def retrieve_table_descriptions(database_name: str, tables: str):
    tables = json.loads(tables)
    table_descriptions = []
    descriptions_path = os.path.join(
        "data/dev/dev_databases", database_name, "database_description"
    )
    for _, _, files in os.walk(descriptions_path):
        for file in files:
            table_name = file.replace(".csv", "")
            if table_name in tables and file.endswith(".csv"):
                table_data = pd.read_csv(os.path.join(descriptions_path, file))
                table_metadata = table_data.to_dict(orient="records")
                table_descriptions.append(
                    {
                        "table_name": table_name,
                        "columns": table_metadata,
                    }
                )
    formatted_descriptions = "Database Descriptions:\n\n"
    for table in table_descriptions:
        formatted_descriptions += f"Table: {table['table_name']}\n"
        for column in table["columns"]:
            formatted_descriptions += (
                f"  - Column: {column.get('original_column_name', 'N/A')}\n"
                f"    Description: {column.get('column_description', 'N/A')}\n"
            )
        formatted_descriptions += "\n"
    return formatted_descriptions


def check_query_syntax(query: str) -> str:
    try:
        parsed = sqlfluff.parse(query)
        return "SQL is syntactically correct!"
    except Exception as e:
        return f"SQL syntax error: {e}"


def select_relevant_database(state: State):
    database = retrieve_database_names().split(", ")
    original_question = state["original_question"]

    prompt = f"Given the query: '{original_question}', which of the following databases is most relevant? Your answer must contain only the name of the database and nothing else! {', '.join(database)}"
    response = llm(prompt)

    state["relevant_database"] = response.strip()
    return state


def select_relevant_tables(state: State):
    tables = retrieve_table_names(state["relevant_database"])
    original_question = state["original_question"]

    prompt = f"Given the query: '{original_question}', which of the following database tables are relevant? You must provide the names of the tables as a comma-separated list. {', '.join(tables)}"
    response = llm(prompt)

    # Parse the response into a list
    relevant_tables = [table.strip() for table in response.split(",")]
    state["relevant_tables"] = relevant_tables
    return state


def get_table_descriptions(state: State):
    state["descriptions"] = retrieve_table_descriptions(
        state["database"], json.dumps(state["tables"])
    )
    return state


def generate_sql_query(state: State):
    # Generate a simple SQL query for demonstration purposes
    state["query"] = f"SELECT * FROM {state['tables'][0]} LIMIT 10;"
    return state


def validate_sql_query(state: State):
    state["query"] = check_query_syntax(state["query"])
    return state


def final_result(state: State):
    return {"query": state["query"], "database": state["database"]}


graph_builder.add_node("select_relevant_database", select_relevant_database)
graph_builder.add_node("select_relevant_tables", select_relevant_tables)
graph_builder.add_node("get_table_descriptions", get_table_descriptions)
graph_builder.add_node("generate_sql_query", generate_sql_query)
graph_builder.add_node("validate_sql_query", validate_sql_query)
graph_builder.add_node("final_result", final_result)

graph_builder.add_edge(START, "select_database")
graph_builder.add_edge("select_database", "get_table_names")
graph_builder.add_edge("get_table_names", "get_table_descriptions")
graph_builder.add_edge("get_table_descriptions", "generate_sql_query")
graph_builder.add_edge("generate_sql_query", "validate_sql_query")
graph_builder.add_edge("validate_sql_query", "final_result")
graph_builder.add_edge("final_result", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print(value)


if __name__ == "__main__":
    sql_input_file = pd.read_json("data/dev/dev.json")
    question_id = 847
    question = sql_input_file["question"][question_id]
    actual_sql = sql_input_file["SQL"][question_id]

    description = "What is the surname of the driver with the best lap time in race number 19 in the second period?"
    inputs = {"input": question}

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input)
        except:
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break
