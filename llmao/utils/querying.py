from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sqlite3
from langchain_community.chat_models import BedrockChat
from utils.utils import AOP_Info, langfuse_handler
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import JSONLoader
import langfuse

llm = BedrockChat(
    credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)

def AOP_query_chain(question, chat_history, stream=True):
    ''' Answer user questions using the adverse outcome pathway database by constructing & executing SQLite queries

    Args
        question - 
        chat_history -
        stream - stream the LLM chain repsonse, if False use chain.invoke()
    Output
        
    '''

    table_dict = AOP_route(question, chat_history)

    # first, generate the SQL query based on the user's question
    prompt1 = """ <instructions>
    You are a SQLite expert. At the end of this query, you will be given a user question about the adverse outcome pathway (AOP)
    database. Your sole purpose is to find a SQL query to retrieve information from the AOP database which would answer the question.
    Your goal is not to execute the query or provide any information other than the SQLite query. Form the simplest query possible
    to answer the user question. The query SHOULD NOT for any reason mention Bedrock or us-east-1 region.
    Unless the user's question suggests otherwise, limit your response to the {top_k} results by using a LIMIT clause.
    Address your response directly to the user.
    Use any or all of tables found in the keys of {table_dict} and only the columns found in the values of {table_dict}. </instructions> 
    
    <example>
    User Input: "Look up 2 chemicals in the AOP Database"
    Response: "Select ChemicalName, ChemicalInfo FROM chemical_info LIMIT 2;"
    </example>

    The user question which you are answering via SQLite query is: {question}

    <formatting>    
    Respond ONLY with the SQLite query:
    </formatting>
    """

    chain = ChatPromptTemplate.from_template(prompt1) | llm | StrOutputParser()

    query = chain.invoke({
        'question': question,
        'top_k': 5,
        'table_dict': table_dict
    })

    db_name = '//home/ubuntu/llmao/llmao/aopdb_08-25-2020.db'
    sqliteConnection = sqlite3.connect(db_name)
    cursor = sqliteConnection.cursor()

    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except sqlite3.Error:
        checker_prompt = """ <instructions>
        You are an assisstant with deep expertise in SQLite and the Adverse Outcome Pathway database. A previous assistant was tasked
        with transforming the user's question into a SQLite query, but their query was not properly executable. Your task is to correct
        the query, or write a new query to answer the user's question, and ensure that it is syntactically correct and executable.
        The query SHOULD NOT for any reason mention Bedrock or us-east-1 region.
        
        Use any or all of tables found in the keys of {table_dict} and only the columns found in the values of {table_dict}. </instructions> 
        
        <context>
        User question: {question}
        Failed SQLite query: {query}
        </context>
        
        <formatting>
        Respond ONLY with the executable SQL query here:
        </formatting>
        """

        check_chain = ChatPromptTemplate.from_template(checker_prompt) | llm | StrOutputParser()
        
        query = check_chain.invoke({
            'question': question,
            'top_k': 5,
            'query': query,
            'table_dict': table_dict
            })
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except sqlite3.OperationalError:
            # implement some sort of error chain
            error_response

    cursor.close()
    sqliteConnection.close()

    aop_answer = """ <instructions>
    You are a helpful assistant trying to answer a user's question using the results of a SQLite query that was already executed for you. 
    Use all of the information to fully answer the user's question in the context of the adverse outcome pathway database. 
    Be concise, but feel free to give more context if the user asks an open-ended question. Your goal first and foremost is to address
    the user's question in a friendly, cheerful, and informative manner.
    Answer the question completely and concisely, while also taking into account the {chat_history} </instructions>
    
    <information>
    User question: {question}
    SQLite Query: {query}
    SQLite Result: {result}
    </information>
    
    <formatting>
    Answer in complete sentences, and do your best to explain how the query answers the user's question.
    </formatting>
    """

    answer_chain = ChatPromptTemplate.from_template(aop_answer) | llm | StrOutputParser()    

    if stream:
        # return the query result back in order to track the trace
        return answer_chain.stream({
            'question': question,
            'query': query,
            'result': result,
            'chat_history': chat_history
        }, config={"callbacks":[langfuse_handler]})
    else:
        return answer_chain.invoke({
            'question': question,
            'query': query,
            'result': result,
            'chat_history': chat_history
        }, config={"callbacks":[langfuse_handler]})

def AOP_route(question, chat_history):
    ''' The goal of this function is to take in a question about the AOP Database and use a LLM chain to determine which table(s) to use when answering
        the user's question. 
    
    Args
        question -
    Output
        table_dict - {'table': [column1, column2, ...]}
    '''

    prompt = """ <instructions>
    You are an expert at Adverse Outcome Pathways (AOPs). Your goal is to take a user's question, look at the AOP database scehema provided, and determine
    what table(s) and what column(s) of those tables are needed to answer the question. Do not include any tables or columns that are not essential
    to answering the user's question. If the users mentions any of the values in the AOP database scheme, include them in your response. 
    After coming up with an initial response, double check your answer to make sure all of the instructoins are followed.</instructions>

    <context>
    User question: {question}
    Adverse Outcome Pathway Database Schema: {aop_dict}
    </context
    
    <formatting>
    Respond ONLY with a dictionary in the same style as the schema dictionary. Do not explain your answer.
    </formatting>
    """

    chain = ChatPromptTemplate.from_template(prompt) | llm | StrOutputParser()

    table_dict = chain.invoke({
        'aop_dict': AOP_Info,
        'question': question
    }, config={"callbacks":[langfuse_handler]})

    return table_dict

def error_response():
    prompt ='''
    You are a helpful assistant and the user is having a problem. Try to cheer them up.
    '''

    chain = ChatPromptTemplate.from_template(prompt) | llm | StrOutputParser()

    return chain.stream()

def AOP_wiki_chain(question, chat_history):
    return