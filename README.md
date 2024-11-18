# LLMsAgents-TextToSQL
Repository for an agent-based system that converts natural language queries to SQL

## IMPORTANT: Document everything using LangSmith

### Setup
This project uses poetry for dependency management, so make sure you have it installed. After that, simply run `make initial-setup` from the root directory of the project.

The test_bird.py file in the setup folder is called from within the setup.py script and contains sample code to establish a connection to the sqlite databases and execute queries against them.

Paper:

- CodeS: https://arxiv.org/abs/2402.16347
- Bird: https://arxiv.org/abs/2305.03111
- ChaseSQL: https://arxiv.org/abs/2410.01943

### Basic structure
1. One `Creator agent` responsible for creating and syntactically validating queries.
2. If a query is not correct, a second `Fixer Agent` is called which provides suggestions on the query. 
3. Then, a last agent is called which is named `Feedback Agent` which can execute the query against the database and provide feedback based on comparing the results to the natural language prompt given by the first agent. 
4. The first agent then revises the query, validates it and then follows steps 2 and 3 again.

### Interfaces between agents
All communication between agents will be string based. The following list describes what each string from to agents should contain.
- Creator to Fixer: The natural language prompt, the query and the error message.
- Fixer to creator: Advisement on how to fix the query
- Creator to feedback: Syntactically correct query, prompt
- Feedback to creator: Suggestions on query improvement based on requests to table

### Actions of each agent
#### Creator
- Create query
- Syntactically check query
- Call other agents
- Retrieve information about tables
#### Fixer
- Provide feedback on syntax of query
- Call Creator agent
#### Feedback
- Send query to database
- Provide feedback based on query results comparison

### Purpose: Multi-Agent vs. Single-Agent
Demonstrating that a multi agent approach leads to more efficient and more correct results.