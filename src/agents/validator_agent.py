from langchain.schema import HumanMessage, SystemMessage, AIMessage


class ValidatorAgent:
    # Initilializes the agent and prepares the system message if available
    def __init__(self, system=""):
        self.system = system
        self.messages = []ystem:
            self.messages.append(SystemMessage(content=system))

    # Logic when calling the agent
    def __call__(self, mesrun       self.messages.append(HumanMessage(content=message))
        result = self.execute()
        self.messages.append(AIMessage(content=result))
        return result

    # invoking the LLM with the collected messages and returning the completion
    def execute(self):
        completion = chat_model.invoke(self.messages)
        return completion.content

__