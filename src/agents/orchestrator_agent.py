from state_types import State
from langgraph.graph import StateGraph, START, END
from langchain_openai import OpenAI
import os
import pandas as pd
import json
import sqlfluff
from dotenv import load_dotenv
from fixer_agent import FixerAgent
from feedback_agent import FeedbackAgent

from creator_agent import generate_sql_query_creator

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


def retrieve_table_descriptions(database_name: str, tables: list):
    table_descriptions = {}
    descriptions_path = os.path.join(
        os.getenv("DB_DIRECTORY"), database_name, "database_description"
    )
    for table_name in tables:
        file_path = os.path.join(descriptions_path, f"{table_name}.csv")
        if os.path.exists(file_path):
            table_data = pd.read_csv(file_path, encoding="utf-8-sig")
            columns = table_data[["original_column_name", "column_description"]]
            table_descriptions[table_name] = []
            for column in columns.itertuples():
                table_descriptions[table_name].append(
                    f"{column.original_column_name}: {column.column_description}"
                )
    return table_descriptions


def initialize_state(state: State):
    state["relevant_database"] = ""
    state["relevant_tables"] = {}
    state["original_question"] = state["messages"][0].content
    state["query"] = ""
    state["feedbacks"] = []
    state["errors"] = []
    state["final_query"] = None
    return state


def select_relevant_database(state: State):
    databases = retrieve_database_names().split(", ")
    original_question = state["original_question"]

    prompt = f"Given the query: '{original_question}', which of the following databases is most relevant? Your answer must contain only the name of the database and nothing else! {', '.join(databases)}"
    response = llm.invoke(prompt)

    state["relevant_database"] = response.strip()
    for table_name in retrieve_table_names(state["relevant_database"]):
        state["relevant_tables"][table_name] = {}
    return state


# TODO - Include database information in the prompt and see how the model performs
def select_relevant_tables(state: State):
    tables = list(state["relevant_tables"].keys())
    original_question = state["original_question"]

    prompt = f"""You are a database assistant responsible for selecting the relevant tables for a given natural language query.
            As input, you will receive the following information:

            {{
                "original_question": "The question that the SQL query is supposed to answer.",
                "tables": "A list of tables you are supposed to choose from."
            }}


            -------------------------------------------------------------------------------

            Here's the process you will follow:
            You will look at the list of tables and the query and determine which tables may be relevant for the query.

            Output Format is the following JSON document:

            {{
                "tables": ["The tables you think will be relevant for the query."]
            }}

            Your response must only consist of the following:
            tables: The tables you think are necessary for the query.

            Ensure that your output is a valid JSON and uses double quotes for strings.
            Your output should not contain any additional information other than the tables you think are relevant in the specified format.
            You must ensure that this is the case.

            -------------------------------------------------------------------------------

            Example Input:
            {{
                "original_question": "What is the surname of the driver with the best lap time in race number 19 in the second qualifying period?",
                "tables": ["circuits", "status", "drivers", "driverStandings", "races", "constructors", "constructorResults", "lapTimes", "qualifying", "pitStops", "seasons", "constructorStandings", "results"]
            }}

            Example Output:
            {{
                "tables": ["drivers", "qualifying"]
            }}

            Another Example Output:
            {{
                "tables": ["drivers", "driverStandings", "races", "results"]
            }}

            As you can see, none of the example outputs actually contain the word output so you must also not include it in your response.

            -------------------------------------------------------------------------------

            Input:

            {{
                "original_question": "{original_question}",
                "tables": {json.dumps(tables)}
            }}
    """
    response = llm.invoke(prompt)
    response = response.replace("Output:", "").strip()

    try:
        # Parse the JSON response
        response_json = json.loads(response)
        relevant_tables = response_json.get("tables", [])
        # Set the elements in the tables part of the JSON as the keys of the state["relevant_tables"] dict
        state["relevant_tables"] = {table: "" for table in relevant_tables}
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}, Response: {response}")
        state["relevant_tables"] = {}

    return state


def get_table_descriptions(state: State):
    state["relevant_tables"] = retrieve_table_descriptions(
        state["relevant_database"], list(state["relevant_tables"].keys())
    )
    return state


def generate_sql_query(state: State):
    return generate_sql_query_creator(state)


def validate_sql_query(state: State):
    try:
        sqlfluff.parse(state["sql_query"])
        return True
    except Exception as e:
        state["errors"].append(str(e))
        return False


def fix_sql_query(state: State):
    fixer_agent = FixerAgent(llm=llm)
    fixer_agent.analyse_incorrect_query(state)
    return state


def feedback_sql_query(state: State):
    feedback_agent = FeedbackAgent(llm=llm)
    feedback_agent.evaluate_query(state)
    return state


def final_result(state: State):
    state["final_query"] = state["sql_query"]
    return state


graph_builder.add_node("initialize_state", initialize_state)
graph_builder.add_node("select_relevant_database", select_relevant_database)
graph_builder.add_node("select_relevant_tables", select_relevant_tables)
graph_builder.add_node("get_table_descriptions", get_table_descriptions)
graph_builder.add_node("generate_sql_query", generate_sql_query)
graph_builder.add_node("fixer_agent", fix_sql_query)
graph_builder.add_node("feedback_agent", fix_sql_query)
graph_builder.add_node("final_result", final_result)

graph_builder.add_edge(START, "initialize_state")
graph_builder.add_edge("initialize_state", "select_relevant_database")
graph_builder.add_edge("select_relevant_database", "select_relevant_tables")
graph_builder.add_edge("select_relevant_tables", "get_table_descriptions")
graph_builder.add_edge("get_table_descriptions", "generate_sql_query")
graph_builder.add_conditional_edges(
    "generate_sql_query",
    validate_sql_query,
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
        with open("src/agents/workflow.png", "wb") as f:
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


def create_sql_from_natural_text(natural_text: str):
    for event in graph.stream({"messages": [("user", natural_text)]}):
        for _, value in event.items():
            for sub_key, sub_value in value.items():
                if sub_key == "final_query" and sub_value:
                    return sub_value
    return "Final Query was not generated"


if __name__ == "__main__":
    sql_input_file = pd.read_json("data/dev/dev.json")
    question_id = 847
    question = sql_input_file["question"][question_id]
    actual_sql = sql_input_file["SQL"][question_id]

    stream_graph_updates(question)
