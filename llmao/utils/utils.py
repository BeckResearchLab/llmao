import sqlite3
from langfuse.callback import CallbackHandler
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Add examples questions: queries here
Queries = {
    'Look up 2 chemicals in the AOP database':'SELECT ChemicalName, ChemicalID from chemical_info LIMIT 2;',
}

# Question bank for random question button
Questions = list(Queries.keys())

# query to get all tables and columns from the AOP database
info_query = """
    SELECT m.name as tableName, 
    p.name as columnName
    FROM sqlite_master m
    left outer join pragma_table_info((m.name)) p
    on m.name <> p.name
    order by tableName, columnName
    ;
    """

# connect to db, execute query, and close connection
db_name = '../aopdb_08-25-2020.db'
sqliteConnection = sqlite3.connect(db_name)
cursor = sqliteConnection.cursor()
cursor.execute(info_query)
info_dict = cursor.fetchall()
cursor.close()
sqliteConnection.close()
AOP_Info = {}

for entry in info_dict:
    table = entry[0]
    # if the table has already been added to the AOP dictionary
    if table in AOP_Info:
        AOP_Info[table].append(entry[1])
    # else create a dictionary entry for the table
    else:
        AOP_Info[table] = [entry[1]]

def get_session():
    '''
    get user session id
    '''
    try:
        runtime = get_instance()
        session_id = get_script_run_ctx().session_id
        session_info = runtime._session_mgr.get_session_info(session_id)
        if session_info is None:
            raise RuntimeError("Couldn't get your Streamlit Session object.")
        return str(session_info.session)
    except RuntimeError:
        pass

langfuse_handler = CallbackHandler(
    public_key=st.secrets['public_key'],
    secret_key=st.secrets['secret_key'],
    host="https://cloud.langfuse.com", # 🇺🇸 US region
    session_id = get_session()
)

def SQL_context_parser(llm, query, query_results):
    '''
    Build a full and complete sentence based off SQLite query, and query_results
    '''
    prompt = """ <instructions>
    You are an expert in both adverse outcome pathways and SQLite queries. You will be given a SQLite query
    and the results of that SQLite query when executed on the adverse outcome pathway database. Your goal is
    to take the context given in order to construct a full and complete sentence that explains the query and the results.
    Do not refer to any information that is not explicitly referenced in the context. </instructions>

    <context> 
    SQLite Query: {query}
    SQLite Query Results: {results}
    """

    chain = ChatPromptTemplate.from_template(prompt) | llm | StrOutputParser()

    return chain.invoke({
        "query": query,
        "results": query_results
    })