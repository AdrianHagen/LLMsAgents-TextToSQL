from tools.database import Database, list_databases
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
# Line below not needed because fixer does not use any tools
# TODO - Should the fixer use any tools?
# from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, PromptTemplate
import os
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent
from langchain_ollama.chat_models import ChatOllama
import json
load_dotenv()



template = """
You are a socalled "SQL fixer" agent, meaning look at how to fix a syntactically incorrect SQL query to become syntactically correct.
The SQL creator agent, which generated the syntactically incorrect SQL query, has already indentified that its generated SQL query is syntactically incorrect. 
Therefore, the SQL creator agent provides you with the incorrect SQL query itself,
the respective database table(s) in which the information requested by the user in the natural language prompt can be found,
the respective error message for the specific error that occured first after the syntactically incorrect SQL query had been run,
and the natural language prompt (original question) from the user.
Your task is it to give the SQL generator agent advise on how to correct the error that occured first to it after it had run the syntactically incorrect SQL query.


-------------------------------------------------------------------------------

Here's the process you will follow:


Steps to perform:
Analysis: Analyse the syntactically incorrect SQL query only syntactically, based on the received error message and also the respective database table(s) in which the information requested by the user in the natural language prompt can be found.
Further analyse where and what changes need to be made in order to fix the specific error that occured first after the syntactically incorrect SQL query had been run by the SQL creator agent and for which it got an error message.
Advise: Provide detailed advise on:
1. Which statement/ part of the SQL query needs to be corrected (e.g., SELECT, WHERE, FROM, etc.) based on the received error message for the specific error.
2. Name the specific error that occured first after the syntactically incorrect SQL query had been run by the SQL creator agent and for which it got an error message (e.g., 'incorrect_name_of_the_attribute' is incorrect spelling of attribute name , 'incorrect_name_of_the_table' is incorrect spelling of table name, 
missing ';' at the end of the query, missing ',' after attribute name 'attribute_name', missing clause after 'AND', missing WHERE statement, 'incorrect_where_statement' is incorrect spelling of WHERE statement, etc.).
3. Advise on where in the syntactically incorrect SQL query the specific error that occured first after running syntactically incorrect SQL query and how to fix this specific error at the respective position.

Output Format is the following json document:

{{  
    "original_question": "The natural language prompt (original question) from the user received by the SQL creator agent.",
    "syntactically_incorrect_sql_query": "Syntactically incorrect SQL query which was provided to you by SQL creator agent.",
    "error_message": "The received error message for the specific error that occured first after the syntactically incorrect SQL query had been run by the SQL creator agent and which was provided to you by this SQL creator agent.",
    "error_position": "Name the statement/ part that needs to be corrected, meaning at which position the specific error can be found, in the syntactically incorrect SQL query here."
    "specific_error":  "Name the specific error that has been made by the SQL creator agent which lead to the SQL query to be syntactically incorrect here.",
    "advise": "Your detailed advise on at which position in the syntactically incorrect SQL query the specific error is located and how to fix this specific error."
}}

Your response must include:
Natural Language Prompt/ Original Question: The natural language prompt (original question) from the user received by the SQL creator agent.
Syntactically Incorrect SQL Query: The syntactically incorrect SQL query provided to you by the SQL creator agent.
Error Message: The error message provided to you by the SQL creator agent which it received after running the syntactically incorrect SQL query.
Error Position: The statement/ part identified by you that needs to be corrected in the syntactically incorrect SQL query.
Specific Error: The specific errors identified by you in the syntactically incorrect SQL query.
Advise: Specific, yet detailed, and actionable advise on where and how to improve the error that occured after the syntactically incorrect SQL query had been run.


Final Notes:
Be precise and thorough in your analysis.
Ensure that the advise is constructive and enables the SQL creator agent to improve iteratively.
And use valid json format.

-------------------------------------------------------------------------------

Example Input:
Syntactically Incorrect SQL Query: "SELECT SUM(revenue) FORM sales WHERE year = 2023;"
Database Table(s): "sales"
Error Message: "ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'FORM sales WHERE year = 2023' at line 1"
Natural Language Prompt/ Original Question: "What is the total revenue generated in 2023?"


Example Output:
{{  "original_question": "What is the total revenue generated in 2023?"
    "syntactically_incorrect_query": "SELECT SUM(revenue) FORM sales WHERE year = 2023;"
    "error_message": "ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'FORM sales WHERE year = 2023' at line 1"
    "error_positions": "Syntax error in FROM statement."
    "specific_errors": "'FORM' is incorrect spelling of FROM statement."
    "advise": "In the FROM statement, replace 'FORM' with 'FROM' to make the query executable with respect to this specific syntax error."
}}

-------------------------------------------------------------------------------


Input:

Syntactically Incorrect SQL Query: {syntactically_incorrect_query}
Database table(s): {database_tables}
Error Message: {error_message}
Original Question: {original_question}


"""

# Prompt the LLM with the template created above
prompt = PromptTemplate.from_template(template)

# Choose the LLM model which is prompted with the template
llm = ChatOllama(model="mistral")

# Define the function to analyse the syntactically incorrect SQL query (as described in the template above)
def analyse_query_syntactically(syntactically_incorrect_query: str, database_tables: str, error_message: str, original_question: str):

    database = Database(database_tables)

    # Line below not needed here because fixer does not execute queries:
    #results = db.execute_query(generated_sql_query)  

    p = prompt.invoke(
        input={"syntactically_incorrect_query": syntactically_incorrect_query, "database_tables": database, "error_message": error_message, "original_question": original_question})

    return llm.invoke(p)

    
# TODO - Replace the space with input to test the function
result = analyse_query_syntactically(" ")

parsed_result = json.loads(result.content)
print(parsed_result)