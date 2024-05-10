from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sqlite3
from langchain_community.chat_models import BedrockChat
from utils.utils import AOP_Info, Queries
import pandas as pd
from ast import literal_eval
import numpy as np
from langchain_core.runnables import RunnablePassthrough

llm = BedrockChat(
    credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)

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

def Chat_Evaluator(question, chat_history):
    '''
    Evaluate user satisfaction based on chat history
    args
        user question
        chat history
    returns
        no returns, (current human question, previous AI response, and rating) are written to /llmao/data/chat_eval.csv
    '''

    prompt = ''' <instructions> 
    You are a friendly assistant given a chat history between a human user and a large language model chatbot. Your goal is to
    evaluate, based on the chat history, whether or not the user is satisfied with the performance of the large language model.
    Pay attention to indicators including, but not limited to: how the user's tone changes throughout the converastion, whether or not their questions are answered sufficiently,
    and whether the user is repeating similar questions multiple times. You will rate the conversation history on a scale of -1 - 1 based
    on the criterion below: </instructions>

    <context>
    Chat history: {chat_history}
    Current question: {question}
    Rating criteria:
        -2 - The user is deeply unsatisfied with their conversation, their questions are not answered whatsoever, they are not happy.
        -1 - The user is somewhat unsatisfied with their conversation, their questions are not fully answered, etc.
        0 - No chat history, the user is neutral towards their conversation, or not enough information to determine
        1 - The user is somewhat satisfied with their conversation, their questions are mostly answered
        2 - The user is very satisfied with their conversation, their questions are fully answered
    </context>

    <formatting> Output ONLY your rating for the user satisfaction based on the rating scale & criteria above. Do not respond
    with anything other than the user satisfaction rating: </formatting>
    '''

    llm = BedrockChat(
        credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)

    chain = ChatPromptTemplate.from_template(prompt) | llm | StrOutputParser()
    
    rating = chain.invoke({
        'question': question,
        'chat_history': chat_history
    })

    # user question, ai_resposne, rating
    if len(chat_history) >= 2:
        with open("/home/ubuntu/llmao/llmao/data/chat_eval.csv","a") as rating_file:
            rating_file.write((str(chat_history[-1]) + ',' + str(chat_history[-2]) + ',' + str(rating)) + "\n")
    else:
        pass
    return    

def AOP_Query_Evaluator(question, query):
    '''
    Evaluate whether the SQLite query provided sufficiently answers the provided user question
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

