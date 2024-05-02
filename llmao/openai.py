import os
from langchain_openai import OpenAI, OpenAIEmbeddings
# from langchain_core.prompts import PromptTemplate
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain


# INSERT YOUR OPENAI API KEY: https://platform.openai.com/docs/models , make an account
os.environ["OPENAI_API_KEY"] = ''

llm = OpenAI()


#db_name = 'sqlite:///aopdb_gene_interactions_08-25-2020.db'
db_name = 'sqlite:///aopdb_08-25-2020.db'
db = SQLDatabase.from_uri(db_name)
print(db.get_usable_table_names())


agent_executor = create_sql_agent(llm, db=db, verbose=True)
agent_executor.invoke(
  'list two chemical that are in the database' )
