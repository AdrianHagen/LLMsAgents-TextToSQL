from state_types import State
from langgraph.graph import StateGraph, START, END
from langchain_openai import OpenAI
import os
import pandas as pd
import json
import chardet
from dotenv import load_dotenv
from feedback_agent import FeedbackAgent
from fixer_agent import FixerAgent
import prompt_templates.select_relevant_database as select_relevant_database_templates
import prompt_templates.select_relevant_tables as select_relevant_tables_templates
from langchain.prompts import PromptTemplate
from creator_agent import create_sql_query_creator
from tools.database import Database

load_dotenv()


graph_builder = StateGraph(State)
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def retrieve_database_names():
    for _, dirs, _ in os.walk(os.getenv("DB_DIRECTORY")):
        return ", ".join(dirs)


def retrieve_table_names(database_name: str):
    table_names = []
    tables_path = os.path.join(
        os.getenv("DB_DIRECTORY"), database_name, "database_description"
    )
    for _, _, files in os.walk(tables_path):
        for file in files:
            if file.endswith(".csv"):
                table_names.append(file.replace(".csv", ""))
    return table_names


def retrieve_column_names(database_name: str, tables: list):
    table_descriptions = {}
    descriptions_path = os.path.join(
        os.getenv("DB_DIRECTORY"), database_name, "database_description"
    )

    for table_name in tables:
        file_path = os.path.join(descriptions_path, f"{table_name}.csv")
        if os.path.exists(file_path):
            # Detect encoding dynamically since it can vary from file to file
            with open(file_path, "rb") as file:
                result = chardet.detect(file.read())
                detected_encoding = (
                    result["encoding"] if result["encoding"] else "utf-8"
                )

            # Use the detected encoding to read the file
            table_data = pd.read_csv(file_path, encoding=detected_encoding)

            # Extract column descriptions
            columns = table_data[["original_column_name", "column_description"]]
            table_descriptions[table_name] = [
                f"{column.original_column_name}" for column in columns.itertuples()
            ]

    return table_descriptions


def initialize_state(state: State):
    state["relevant_database"] = ""
    state["relevant_tables"] = {}
    state["original_question"] = state["messages"][0].content
    state["generated_sql_queries"] = []
    state["feedbacks"] = []
    state["errors"] = []
    state["final_query"] = None
    return state


def select_relevant_database(state: State):
    databases = retrieve_database_names().split(", ")

    prompt = PromptTemplate.from_template(select_relevant_database_templates.ZERO_SHOT)
    prompt = prompt.invoke(
        {
            "original_question": state["original_question"],
            "databases": databases,
            "feedback_trace": json.dumps(state["feedbacks"]),
        }
    )
    response = llm.invoke(prompt)

    state["relevant_database"] = response.strip().lower()
    for table_name in retrieve_table_names(state["relevant_database"]):
        state["relevant_tables"][table_name] = {}
    return state


# TODO - Include database information in the prompt and see how the model performs
def select_relevant_tables(state: State):
    tables = list(state["relevant_tables"].keys())
    original_question = state["original_question"]

    prompt = PromptTemplate.from_template(select_relevant_tables_templates.TWO_SHOT)
    prompt = prompt.invoke(
        {
            "original_question": original_question,
            "tables": tables,
            "feedback_trace": json.dumps(state["feedbacks"]),
        }
    )
    raw_response = llm.invoke(prompt)
    # Sometimes the LLM starts the response with some extra text, so we remove it
    processed_response = raw_response[
        raw_response.find("{") : raw_response.rfind("}") + 1
    ].strip()

    try:
        # Parse the JSON response
        response_json = json.loads(processed_response)
        relevant_tables = response_json.get("tables", [])
        # Set the elements in the tables part of the JSON as the keys of the state["relevant_tables"] dict
        state["relevant_tables"] = {table: "" for table in relevant_tables}
    except json.JSONDecodeError as e:
        print(
            f"""Orchestrator Agent: Failed to decode JSON response: {e}, 
            raw Response: {raw_response}, 
            processed Response: {processed_response}"""
        )
        state["relevant_tables"] = {}

    return state


def get_table_column_names(state: State):
    state["relevant_tables"] = retrieve_column_names(
        state["relevant_database"], list(state["relevant_tables"].keys())
    )
    return state


def create_sql_query(state: State):
    return create_sql_query_creator(state)


def validate_sql_query_syntax(state: State):
    db = Database(state["relevant_database"])
    try:
        db.execute_query(state["generated_sql_queries"][-1])
        return True
    except Exception as e:
        state["errors"].append(f"Error executing query: {e}")
        return False


def validate_sql_query(state: State):
    return state["feedbacks"][-1]["is_correct"]


def fix_sql_query(state: State):
    fixer_agent = FixerAgent(llm=llm)
    fixer_agent.analyse_incorrect_query(state)
    return state


def feedback_sql_query(state: State):
    feedback_agent = FeedbackAgent(llm=llm)
    feedback_agent.evaluate_query(state)
    return state


def final_result(state: State):
    state["final_query"] = state["generated_sql_queries"][-1]
    return state


graph_builder.add_node("initialize_state", initialize_state)
graph_builder.add_node("select_relevant_database", select_relevant_database)
graph_builder.add_node("select_relevant_tables", select_relevant_tables)
graph_builder.add_node("get_table_column_names", get_table_column_names)
graph_builder.add_node("creator_agent", create_sql_query)
graph_builder.add_node("fixer_agent", fix_sql_query)
graph_builder.add_node("feedback_agent", feedback_sql_query)
graph_builder.add_node("final_result", final_result)

graph_builder.add_edge(START, "initialize_state")
graph_builder.add_edge("initialize_state", "select_relevant_database")
graph_builder.add_edge("select_relevant_database", "select_relevant_tables")
graph_builder.add_edge("select_relevant_tables", "get_table_column_names")
graph_builder.add_edge("get_table_column_names", "creator_agent")
graph_builder.add_conditional_edges(
    "creator_agent",
    validate_sql_query_syntax,
    {True: "feedback_agent", False: "fixer_agent"},
)
graph_builder.add_edge("fixer_agent", "select_relevant_database")
graph_builder.add_conditional_edges(
    "feedback_agent",
    validate_sql_query,
    {True: "final_result", False: "select_relevant_database"},
)
graph_builder.add_edge("final_result", END)

graph = graph_builder.compile()


def visualize_graph():
    try:
        # Get the PNG image bytes
        png_bytes = graph.get_graph().draw_mermaid_png()

        # Save to a file
        with open(
            os.path.join(os.getenv("SRC_DIRECTORY"), "agents/workflow.png"), "wb"
        ) as f:
            f.write(png_bytes)
    except Exception as e:
        print(f"An error occurred: {e}")


def format_event_output(event):
    formatted_output = ""
    for key, value in event.items():
        formatted_output += f"{key}:\n"
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                formatted_output += f"  {sub_key}: {sub_value}\n"
        else:
            formatted_output += f"  {value}\n"
    return formatted_output


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}):
        formatted_output = format_event_output(event)
        print(formatted_output)


def create_sql_from_natural_text(natural_text: str, max_iterations: int = 20):
    """
    Converts natural language text into an SQL query.

    This function takes a natural language input string and processes it through a graph stream to generate an SQL query.
    It listens for events in the graph stream and extracts the final SQL query and the relevant database from the event data.

    Args:
        natural_text (str): The natural language text to be converted into an SQL query.

    Returns:
        tuple: A tuple containing the generated SQL query (str) and the relevant database (str).
               If the final query is not generated, it returns ("Final Query was not generated", "").
    """
    iteration_count = 0

    try:
        for event in graph.stream({"messages": [("user", natural_text)]}):
            iteration_count += 1
            if iteration_count > max_iterations:
                print("Stopping condition reached: Maximum iterations exceeded")
                for _, value in event.items():
                    for sub_key, sub_value in value.items():
                        if sub_key == "generated_sql_queries":
                            return sub_value[-1], value["relevant_database"]

            for _, value in event.items():
                for sub_key, sub_value in value.items():
                    if sub_key == "final_query" and sub_value:
                        return sub_value, value["relevant_database"]
    except Exception as e:
        print(f"Orchestrator Agent: An error occurred: {e}")
        return "", ""

    return "Final Query was not generated", ""


if __name__ == "__main__":
    sql_input_file = pd.read_json("data/dev/dev.json")
    question_id = 847
    question = sql_input_file["question"][question_id]
    actual_sql = sql_input_file["SQL"][question_id]

    stream_graph_updates(question)
