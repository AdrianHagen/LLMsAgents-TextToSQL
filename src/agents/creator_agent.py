from langchain.agents import create_react_agent, Tool, AgentExecutor
from langchain.tools import tool
from langchain_ollama.llms import OllamaLLM
import os
import pandas as pd
import sqlfluff
from langchain_core.prompts import PromptTemplate
import json


def retrieve_database_names():
    """
    Iterate over all tables given as folders in the database and return the names of the tables (folders).
    """
    for _, dirs, _ in os.walk("data/dev/dev_databases"):
        return ", ".join(dirs)


def retrieve_table_names(database_name: str):
    """
    Retrieve the names of all tables in a given database.

    :param database_name: Name of the database.
    :return: Names of all tables in the database.
    """
    table_names = []
    tables_path = os.path.join("data/dev/dev_databases", database_name)

    # Collect table names from the database folder
    for _, dirs, _ in os.walk(tables_path):
        table_names = dirs

    return table_names


def retrieve_table_descriptions(database_name: str, tables: str):
    """
    Retrieve and format the descriptions of specified tables in a given database for LLM input.

    :param database_name: Name of the database.
    :param tables: JSON string representing a list of table names to retrieve descriptions for.
    :return: Formatted descriptions of specified tables in the database.
    """
    tables = json.loads(tables)
    table_descriptions = []
    descriptions_path = os.path.join(
        "data/dev/dev_databases", database_name, "database_description"
    )

    # Collect descriptions from CSV files
    for _, _, files in os.walk(descriptions_path):
        for file in files:
            table_name = file.replace(".csv", "")
            if table_name in tables and file.endswith(
                ".csv"
            ):  # Ensure we're only processing specified CSV files
                table_data = pd.read_csv(os.path.join(descriptions_path, file))
                # Convert the table data to a dictionary for processing
                table_metadata = table_data.to_dict(orient="records")
                table_descriptions.append(
                    {
                        "table_name": table_name,
                        "columns": table_metadata,
                    }
                )

    # Format the output for LLM input
    formatted_descriptions = "Database Descriptions:\n\n"
    for table in table_descriptions:
        formatted_descriptions += f"Table: {table['table_name']}\n"
        for column in table["columns"]:
            formatted_descriptions += (
                f"  - Column: {column.get('original_column_name', 'N/A')}\n"
                f"    Description: {column.get('column_description', 'N/A')}\n"
            )
        formatted_descriptions += "\n"

    print(formatted_descriptions)
    return formatted_descriptions


def check_query_syntax(self, query: str) -> str:
    try:
        # Parse the SQL query using SQLFluff's parser
        parsed = sqlfluff.parse(query)

        # If parsing succeeds without errors, the SQL is considered valid
        return "SQL is syntactically correct!"
    except Exception as e:
        # If parsing fails, the SQL is considered invalid
        return f"SQL syntax error: {e}"


def create_tools():
    """
    Create LangChain tools for the agent.

    :return: List of tools.
    """
    retrieve_table_names_tool = Tool(
        name="DatabaseInformationRetriever.retrieve_table_names",
        func=retrieve_table_names,
        description="Retrieves the names of all tables in a given database. Takes the name of the database as input.",
    )
    retrieve_database_descriptions_tool = Tool(
        name="DatabaseInformationRetriever.retrieve_table_descriptions",
        func=retrieve_table_descriptions,
        description=(
            "Retrieves the descriptions of specified tables in a given database. "
            "Takes the name of the database (string) and a list of table names (formatted as a JSON string)."
        ),
    )
    check_query_syntax_tool = Tool(
        name="SQLQuerySyntaxChecker.check_query_syntax",
        func=check_query_syntax,
        description="Checks the syntax of an SQL query. Takes the SQL query as input.",
    )
    return [
        retrieve_table_names_tool,
        retrieve_database_descriptions_tool,
        check_query_syntax_tool,
    ]


databases = retrieve_database_names()

template = """You are an AI that generates SQL queries based on natural language descriptions. You have access to the following tools:

{tools}

and the following databases:

{databases}

Your task is to generate a correct SQL query based on the input question. Follow these steps **in order**:

1. Select the relevant database
2. Retrieve the table names for the relevant database
3. Select the relevant tables you have just retrieved
4. Retrieve the descriptions of the relevant tables
4. Generate an SQL query based on your gathered information and the original input question
5. Check the query syntax
6. Return the results in json format looking like this {"query": "Your created query", "database": "Your selected database"}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of {tool_names}
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Note that you need to execute queries against the tables in the database you choose in step 1, not the database itself.

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""


# Example usage
if __name__ == "__main__":
    # Create the SQL query generator agent
    llm = OllamaLLM(model="sqlcoder:7b")
    tools = create_tools()
    agent = create_react_agent(llm, tools, PromptTemplate.from_template(template))

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=10,
        verbose=True,
        handle_parsing_errors=True,
    )

    # Example natural language inputs
    description = "Among the schools with the average score in Math over 560 in the SAT test, how many schools are directly charter-funded?"
    inputs = {"input": description, "databases": databases}
    print(agent_executor.invoke(inputs))
