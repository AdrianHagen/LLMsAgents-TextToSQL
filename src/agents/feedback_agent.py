from tools.database import Database, list_databases
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, PromptTemplate
import os
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent
from langchain_ollama.chat_models import ChatOllama
import json
load_dotenv()



template = """
You are a database assistant responsible for verifying the accuracy of a generated SQL query.
Your task is to evaluate whether the results of the query answer the original question.

-------------------------------------------------------------------------------

Here's the process you will follow:


Steps to Perform:
Evaluation: Compare the results of the query to the original question.
Analyze whether the query correctly answers the question in terms of relevance and accuracy.
Feedback: Provide detailed feedback on:
a. Whether the query result correctly answers the question.
b. Any issues or discrepancies found (e.g., incorrect filtering, missing fields, aggregation errors).
c. Suggestions for improving the query if it is incorrect.

Output Format is the following json document:

{{
    "query_result": "Query Result",
    "is_correct": true/false,
    "feedback": "Your detailed feedback here."
}}

Your response must include:
query_result: The result of executing the SQL query.
is_correct: A clear "true" or "false" on whether the query answers the question, followed by an explanation.
Feedback: Specific and actionable suggestions to improve the query, if necessary.


Final Notes:
Be precise and thorough in your evaluation.
Ensure that the feedback is constructive and enables the text-to-SQL model to improve iteratively.
And use valid json format.

-------------------------------------------------------------------------------

Example Input:
Query Result: 123.456
Original Question: "What is the total revenue generated in 2023?"
Database: "sales"
Generated SQL Query: SELECT SUM(revenue) FROM sales WHERE year = 2023;

Example Output:
{{
    "query_result": "123.456"
    "is_correct": true,
    "feedback": "No changes needed. The query is accurate"
}}

-------------------------------------------------------------------------------


Input:

Query Result: {query_result}
Original Question: {original_question}
Database: {database}
Generated SQL Query: {generated_sql_query}


"""

prompt = PromptTemplate.from_template(template)
llm = ChatOllama(model="mistral")

def evaluate_query(original_question: str, database: str, generated_sql_query: str):

    db = Database(database)

    results = db.execute_query(generated_sql_query)

    p = prompt.invoke(
        input={"original_question": original_question, "database": database, "generated_sql_query": generated_sql_query, "query_result": results})

    return llm.invoke(p)

    

result = evaluate_query("Please list the lowest three eligible free rates for students aged 5-17 in continuation schools.", "california_schools", "SELECT `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` FROM frpm WHERE `Educational Option Type` = 'Continuation School' AND `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` IS NOT NULL ORDER BY `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` ASC LIMIT 3")

parsed_result = json.loads(result.content)
print(parsed_result)