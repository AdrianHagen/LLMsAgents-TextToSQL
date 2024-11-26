ZERO_SHOT = """
Given the query: '{original_question}', which of the following databases is most relevant?

{databases}

Note that there might have been 0 or more previous runs of a model that tried to generate a query.
You will be given the FeedbackResponse from the previous run to help you make a decision.
It is however highly unlikely that you will need to use this information to make a decision.
You should therefore only use it if it clearly indicates that previously, a wrong database was selected.

Here is the Feedback trace. Note again that if it is empty, you do not need to use it at all:
{feedback_trace}

Your answer must contain only the name of the database and nothing else!
"""
