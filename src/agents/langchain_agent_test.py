from langchain_community.utilities.sql_database import SQLDatabase
from langchain_ollama.llms import OllamaLLM
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from database import Database
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
import os

class SQLAgent:
    def __init__(self, database: Database):
        self.database = database
        self.db_path = database.get_db_path()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
        #self.llm = OllamaLLM(model="mistral")
        self.agent_executor = None
        self.initialize_agent()

    def initialize_agent(self):
        """
        Initializes the agent with the SQL database and LLM.
        """
        db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")
        toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
        tools = toolkit.get_tools()

        sql_prefix_answer = """You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
        Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
        You can order the results by a relevant column to return the most interesting examples in the database.
        Never query for all the columns from a specific table, only ask for the relevant columns given the question.
        You have access to tools for interacting with the database.
        Only use the below tools. Only use the information returned by the below tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

        To start you should ALWAYS look at the tables in the database to see what you can query.
        Do NOT skip this step.
        Then you should query the schema of the most relevant tables."""

        sql_prefix_query = """You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the SQL Query you used to obtain these results.
        You must format the returned SQL query in the following way:
        ```sql
        <SQL QUERY>
        ```
        You can order the results by a relevant column to return the most interesting examples in the database.
        Never query for all the columns from a specific table, only ask for the relevant columns given the question.
        You have access to tools for interacting with the database.
        Only use the below tools. Only use the information returned by the below tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

        To start you should ALWAYS look at the tables in the database to see what you can query.
        Do NOT skip this step.
        Then you should query the schema of the most relevant tables."""

        system_message = SystemMessage(content=sql_prefix_query)
        self.agent_executor = create_react_agent(model=self.llm, tools=tools, state_modifier=system_message)

    def generate_query(self, question):
        """
        Generates a SQL query for a given question using the agent.
        Extracts and returns only the SQL query from the response.
        """
        try:
            messages = [{"role": "user", "content": question}]
            
            # Stream the agent's response
            events = self.agent_executor.stream(
                {"messages": messages},
                stream_mode="values",
            )

            response_text = ""
            for event in events:
                # Collect all response messages into a single text
                message = event["messages"][-1]
                if hasattr(message, "content"):
                    response_text += message.content
                else:
                    response_text += message

            # Extract the SQL query from the response
            if "```sql" in response_text:
                start = response_text.find("```sql") + len("```sql")
                end = response_text.find("```", start)
                sql_query = response_text[start:end].strip()
                return sql_query
            else:
                print("SQL query not found in the response.")
                return None

        except Exception as e:
            print(f"Error generating response: {e}")
            return None


    def generate_answer(self, question):
        """
        Generates a SQL query for a given question using the agent.
        Uses the `stream` method to process the response.
        """
        try:
            messages = [{"role": "user", "content": question}]
           
            events = self.agent_executor.stream(
                {"messages": messages},
                stream_mode="values",
            )
            for event in events:
                event["messages"][-1].pretty_print()
        
        except Exception as e:
            print(f"Error generating response: {e}")
            return None