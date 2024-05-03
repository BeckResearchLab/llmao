import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter
from langchain_community.llms import Bedrock
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
#from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

st.set_page_config(page_title='llmao')
st.title('llmao')

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# conversation
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    else:
        with st.chat_message("AI"):
            st.markdown(message.content)

# create an introductory llm call to classify the user question
def route(human_question, chat_history, info):
    intro_prompt =  PromptTemplate.from_template("""
        Given the user question below, classify whether it requires executing a query within the
        adverse outcome pathway (AOP) database or not. If it requires executing a query, respond with 'Database'.
        otherwise respond with 'None'.
        Do not respond with more than one word.

        <question>
        {question}
        </question>

        Classification:"""
        )

    #route_chain
    
    if 'database' in info["topic"].lower():
        # get table names
        # enter sql chain
        return generate_sql_response()

# define a function to generate SQL responses if necessary
def generate_response(human_question, chat_history):
    template = """
    You are a helpful assistant. Answer the following questions considering the chat history and user question

    Chat history: {chat_history}

    question: {user_question}
    """
   
    prompt = ChatPromptTemplate.from_template(template)


    llm = Bedrock(
        credentials_profile_name="default", model_id="mistral.mistral-7b-instruct-v0:2", verbose=True)

    #chain = prompt | llm | StrOutputParser()

    db_name = 'sqlite:///aopdb_08-25-2020.db'
    db = SQLDatabase.from_uri(db_name)

    write_query = create_sql_query_chain(llm, db)
    execute_query = QuerySQLDataBaseTool(db=db)

    # define a prompt to create answer from the query result
    answer_prompt = ChatPromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, and chat history, answer the user question.

    question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Chat History: {chat_history}
    Answer: """
    )

    # # define a subchain to create the answer from the query result
    answer = answer_prompt | llm | StrOutputParser()

    # define the chain
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
       | answer
    )

    return chain.stream({
        "chat_history": chat_history,
        "question": human_question
    })

human_question = st.chat_input("Your message")
if human_question is not None and human_question != "":
    st.session_state.chat_history.append(HumanMessage(human_question))

    with st.chat_message("Human"):
        st.markdown(human_question)

    with st.chat_message("AI"):
        ai_response = st.write_stream(generate_response(human_question, st.session_state.chat_history))

    st.session_state.chat_history.append(AIMessage(ai_response))
