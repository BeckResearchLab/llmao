from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sqlite3
from langchain_community.chat_models import BedrockChat
from utils.utils import AOP_Info, Queries
import pandas as pd
from ast import literal_eval
import numpy as np
from langchain_core.runnables import RunnablePassthrough

def Generator(n=5, k=5, dict=True):
    '''
    generate AOP questions and corresponding SQLite queries
    args
        n - number of question:query pairs to output, default 5
        k - # of results used for SQLite LIMIT statement, default 5
    returns
        data - dictionary {question:query} or 
            pandas dataframe, column 1 is the question and column 2 is the SQLite query
    '''

    llm = BedrockChat(
        credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)


    generate_prompt = """ <instructions>
    You are an expert at adverse outcome pathways (AOP) and SQLite databases; you have familiarity with executing SQLite queries
    over the AOP database. Now, imagine you are another  AOP expert interested in asking advanced, high level questions about the AOP database.
    Your goal is to come up with {n} questions that an AOP database expert would have about the AOP database. Next, you should come up with a SQLite query on the AOP database to answer
    the user's question using information about the AOP database. Do not write queries that select unnecessary data; use a LIMIT statement
    to restrict your queries to the {top_k} results unless the questions implies otherwise. </instructions>

    <example>
    Sample questions are as shown in: {examples}
    </example>

    <context>
    AOP database dictionary: {aop_dict}
    </context>

    <formatting>
    Output your answer only in the format of a python dictionary, where the dictionary key is the user question and the value of each
    key is the corresponding SQLite query. Only respond with the dictionary in correct python syntax such that it can be directly
    ran in code. Ensure all quotation marks are matched appropriately.
    </formatting>
    """

    # validate the python dictionary from generate_prompt is syntactically correct
    check_prompt = """" <instructions>
    You are a Python programming expert, particularly skilled at working with dictionaries. You will be passed a python3 dictionary
    and your sole goal is to ensure that the dictionary is syntactically correct and valid python code. Ensure all strings are properly
    enclosed within a set of matching quotation marks. Only make changes that are syntactically necessary.</instructions>
    
    <context> dictionary: {question_dict} </context>

    <formatting> Return only the corrected Python dictionary. If the original dictionary is syntactically valid, return the
    original dictionary. Do not respond with any text other than the Python dictionary: </formatting>
    """

    chain = ChatPromptTemplate.from_template(generate_prompt) | llm | RunnablePassthrough(question_dict=StrOutputParser()) | ChatPromptTemplate.from_template(check_prompt) | llm | StrOutputParser()

    response = chain.invoke({
        'aop_dict': AOP_Info,
        'examples': Queries,
        'n': n,
        'top_k': k
    })

    # convert reponse string into a python dictionary
    question_dict = literal_eval(response)
    # return dictionary by default
    if dict:
        return question_dict
    # return dataframe
    else:
        column_names = np.arange(0, len(question_dict.keys()))
        for column in column_names:
            column = 'Q' + str(column)

        keys = list(question_dict.keys())[1::]
        value_dict = list(question_dict.values())[1::]
        values = []
        df_dict = {}
        for i in range(0, len(keys)):
            index = value_dict[i]
            value = index[0]
            values.append(value)
            df_dict[keys[i]] = value

        data = pd.DataFrame()
        data['Question'] = keys
        data['Query'] = values
        return data

def Chat_Evaluator():
    '''
    Evaluate user satisfaction based on chat history
    '''

def AOP_Query_Evaluator(question, query):
    '''
    evaluate whether the SQLite query provided sufficiently answers the provided user question
    args
        question - user input question about the AOP database, str
        query - SQLite query to retrieve relevant response information
    returns
        llm output response 
    '''

    prompt = ''' <instructions>
    You are an expert at adverse outcome pathways (AOP) and SQLite databases; you have familiarity with executing SQLite queries
    over the AOP database. You will be given a user question about the AOP database, and a corresponding query. Your goal is to
    evaluate whether or not the SQLite query fully answers the user's question based on the following criteria: </instructions>

    <context>
    User question: {question}
    SQLite query: {query}
    AOP database schema: {aop_dict}
    Criteria:
        - All columns and tables in the query exist based on the AOP database schema
        - The query is not too complex given the complexity of the question
        - The SQLite query is syntactically executable    
    </context>
    
    <formatting>
    Respond only with True if the above critera are satisfied, otherwise respond with False.
    Only respond with one word:
    </formatting>
    '''

    llm = BedrockChat(
        credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)
    
    chain = ChatPromptTemplate.from_template(prompt) | llm | StrOutputParser()

    return chain.invoke({
        'question': question,
        'query': query,
        'aop_dict': AOP_Info
    })

def Chat_Session_Evaluator(chat_history):
    '''
    '''

    prompt = '''
    '''
    return

    



