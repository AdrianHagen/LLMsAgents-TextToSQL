import json

from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from typing_extensions import TypedDict

from agents.types import FeedbackResponse, State
from tools.database import Database


class FeedbackAgent:

    def __init__(self, llm: BaseChatModel = None) -> None:
        self.template = """
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
                "feedback": "Your detailed feedback here.",
                "updated_query": "The suggested updated query in case the original is incorrect. Return null when correct."
            }}

            Your response must include:
            query_result: The result of executing the SQL query.
            is_correct: A clear "true" or "false" on whether the query answers the question, followed by an explanation.
            feedback: Specific and actionable suggestions to improve the query, if necessary.
            updated_query: An updated sql query based on the feedback. NOT THE ORIGINAL QUERY.

            Final Notes:
            Be precise and thorough in your evaluation.
            Ensure that the feedback is constructive and enables the text-to-SQL model to improve iteratively.

            Use valid JSON only. DO NOT deviate from the given schema.

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
                "updated_query": null
            }}

            -------------------------------------------------------------------------------


            Input:

            Query Result: {query_result}
            Original Question: {original_question}
            Database: {database}
            Generated SQL Query: {generated_sql_query}


            """

        self.prompt = PromptTemplate.from_template(self.template)
        if llm is None:
            self.llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
        else:
            self.llm = llm

    def evaluate_query(self, state: State):
        original_question = state["original_question"]
        database = state["database"]
        generated_sql_query = state["generated_sql_queries"]

        response = self.evaluate_query(original_question, database, generated_sql_query)

        if response is not None:
            state["feedbacks"].append(response)
        else:
            state["errors"].append("Feedback Failed")

    def evaluate_query(
        self, original_question: str, database: str, generated_sql_query: str
    ) -> FeedbackResponse | None:

        db = Database(database)

        results = db.execute_query(generated_sql_query)

        p = self.prompt.invoke(
            input={
                "original_question": original_question,
                "database": database,
                "generated_sql_query": generated_sql_query,
                "query_result": results,
            }
        )

        resposne = self.llm.invoke(p)

        try:
            return json.loads(resposne.content)
        except:
            return None

    if __name__ == "__main__":
        state = {
            "original_question": "Please list the lowest three eligible free rates for students aged 5-17 in continuation schools.",
            "database": "california_schools",
            "generated_sql_queries": "SELECT `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` FROM frpm WHERE `Educational Option Type` = 'Continuation School' AND `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` IS NOT NULL ORDER BY `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` ASC LIMIT 3",
        }

        print(evaluate_query(state))
