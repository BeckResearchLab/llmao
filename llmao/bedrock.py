from operator import itemgetter
from langchain_community.llms import Bedrock
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
#from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


llm = Bedrock(
    credentials_profile_name="default", model_id="mistral.mistral-7b-instruct-v0:2", verbose=True)

db_name = 'sqlite:///aopdb_08-25-2020.db'
db = SQLDatabase.from_uri(db_name)

execute_query = QuerySQLDataBaseTool(db=db)
write_query = create_sql_query_chain(llm, db)

# define a prompt to create answer from the query result
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

# define a subchain to create the answer from the query result
answer = answer_prompt | llm | StrOutputParser()

# define the chain
chain = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query") | execute_query
    )
    | answer
)

print(chain.invoke({"question": "Describe the chemical_gene table"}))
