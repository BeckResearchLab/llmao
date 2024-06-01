from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sqlite3
from langchain_community.chat_models import BedrockChat
from utils.utils import AOP_Info, SQL_context_parser
from utils.utils import get_session
from eval.evaluator import Evaluator
from langfuse.decorators import observe, langfuse_context
from langchain_core.messages import AIMessage


@observe(capture_input=False)
def AOP_query_chain(question, chat_history, save_context=True, stream=True):
    ''' Answer user questions using the adverse outcome pathway database by constructing & executing SQLite queries

    Args
        question - 
        chat_history -
        stream - stream the LLM chain repsonse, if False use chain.invoke()
    Output
    '''
    langfuse_context.update_current_trace(name = "AOP_DB_RAG", session_id=get_session())
    langfuse_context.update_current_observation(name="retrieval", session_id=get_session(), input=question)
    try:
        langfuse_handler = langfuse_context.get_current_langchain_handler()
    except IndexError:
        pass
    table_dict = AOP_route(question, chat_history)

    llm = BedrockChat(
        credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)

    # first, generate the SQL query based on the user's question
    query_generator = """ <instructions>
    You are a SQLite expert. At the end of this query, you will be given a user question about the adverse outcome pathway (AOP)
    database. Your sole purpose is to find a SQL query to retrieve information from the AOP database which would answer the question.
    Your goal is not to execute the query or provide any information other than the SQLite query. Form the simplest query possible
    to answer the user question. The query SHOULD NOT for any reason mention Bedrock or us-east-1 region.
    Unless the user's question suggests otherwise, limit your response to the {top_k} results by using a LIMIT clause.
    Use any or all of tables found in the keys of {table_dict} and only the columns found in the values of {table_dict}. </instructions> 
    
    <example1>
    User Input: "Look up 2 chemicals in the AOP Database"
    Response: "Select ChemicalName, ChemicalInfo FROM chemical_info LIMIT 2;"
    </example1>

    <example2>

    </example2>

    The user question which you are answering via SQLite query is: {question}

    <formatting>    
    Respond ONLY with the SQLite query:
    </formatting>
    """

    chain = ChatPromptTemplate.from_template(query_generator) | llm | StrOutputParser()

    query = chain.invoke({
        'question': question,
        'top_k': 5,
        'table_dict': table_dict
    })

    db_name = './aopdb_08-25-2020.db'
    sqliteConnection = sqlite3.connect(db_name)
    cursor = sqliteConnection.cursor()

    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except sqlite3.ProgrammingError:
        result = "The SQLite query was not valid, the AOP database could not be queried"
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
            result = "The SQLite query was not valid"
            return failed_response(question, chat_history)

    cursor.close()
    sqliteConnection.close()

    if save_context:
        # transform the SQL query + result into full sentence context
        context = SQL_context_parser(llm, query=query, query_results=result)
        langfuse_context.update_current_observation(
            name='aop_db_retrieval',
            input=question,
            output=context,
            tags=["retrieval"]
        )
        AOP_query_chain.context = context
    else:
        pass

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
    
    answer_stream = answer_chain.invoke({
            'question': question,
            'query': query,
            'result': result,
            'chat_history': chat_history
        })

    evaluator = Evaluator(metrics = ['faithfulness', 'answer_relevancy'], data=[[question, answer_stream, context]])
    evaluator.trace_scores()
    
    if stream:
        return answer_chain.stream({
            'question': question,
            'query': query,
            'result': result,
            'chat_history': chat_history
        }, config={"callbacks": [langfuse_handler]})
    else:
        return [answer_chain.invoke({
            'question': question,
            'query': query,
            'result': result,
            'chat_history': chat_history
            }), context]

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

    llm = BedrockChat(credentials_profile_name="default", model_id="mistral.mistral-7b-instruct-v0:2", verbose=True)

    chain = ChatPromptTemplate.from_template(prompt) | llm | StrOutputParser()

    table_dict = chain.invoke({
        'aop_dict': AOP_Info,
        'question': question
    })

    return table_dict

def failed_response(question, chat_history, stream=True):
    prompt ='''
    You are a helpful assisstant who is trying to help a user who asked a question about the
    adverse outcome pathway database. Unfortunately, the user's question could not be answered
    using the adverse outcome pathway database because the information could not be found.
    Given the user context below, explain the situation to the current user and offer some alternatives.
    If the chat history is none, do not mention the chat history.
    
    Context:
    User question: {question}
    Chat history: {chat_history}
    '''
    
    llm = BedrockChat(
        credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)
    #llm = BedrockChat(credentials_profile_name="default", model_id="mistral.mistral-7b-instruct-v0:2", verbose=True)

    chain = ChatPromptTemplate.from_template(prompt) | llm | StrOutputParser()

    if stream:
        return chain.stream({"question": question, "chat_history": chat_history})
    else:
        return chain.invoke({"question": question, "chat_history": chat_history})