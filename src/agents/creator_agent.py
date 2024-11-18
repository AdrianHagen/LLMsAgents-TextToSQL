from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI


class SQLQueryGenerator:
    """
    A class to generate SQL queries based on natural language input.
    """

    def generate_query(self, input_text: str) -> str:
        """
        Generate an SQL query from natural language text.

        :param input_text: Natural language description of the desired query.
        :return: Generated SQL query as a string.
        """
        # For simplicity, this method serves as a placeholder
        # Actual SQL generation is delegated to the LLM via LangChain
        return f"Generating SQL query based on input: '{input_text}'"


class SQLQueryGeneratorAgent:
    """
    A class to create a LangChain agent for generating SQL queries.
    """

    def __init__(self):
        """
        Initialize the SQLQueryGeneratorAgent.
        """
        self.sql_generator = SQLQueryGenerator()
        self.tools = self._create_tools()
        self.agent = self._initialize_agent()

    def _create_tools(self):
        """
        Create LangChain tools for the agent.

        :return: List of tools.
        """
        generate_query_tool = Tool(
            name="SQLQueryGenerator",
            func=self.sql_generator.generate_query,
            description="Generates SQL queries from natural language descriptions.",
        )
        return [generate_query_tool]

    def _initialize_agent(self):
        """
        Initialize the LangChain agent with the tools and an LLM.

        :return: LangChain agent.
        """
        llm = ChatOpenAI(temperature=0)
        return initialize_agent(
            self.tools,
            llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

    def run(self, input_text: str) -> str:
        """
        Run the agent to generate an SQL query based on input text.

        :param input_text: Natural language description of the desired query.
        :return: Generated SQL query.
        """
        return self.agent.run(f"Generate an SQL query for: {input_text}")


# Example usage
if __name__ == "__main__":
    # Create the SQL query generator agent
    agent = SQLQueryGeneratorAgent()

    # Example natural language inputs
    description1 = "Find the names and email addresses of all users who registered in the last 30 days."
    print(agent.run(description1))

    description2 = "Retrieve the total sales for each product in the last year."
    print(agent.run(description2))
