from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sqlite3
from langchain_community.chat_models import BedrockChat
from utils.utils import AOP_Info, Queries

def Generator(n=50):
    '''
    generate AOP questions and corresponding SQLite queries
    args
        n - number of question:query pairs to output
    '''

    llm = BedrockChat(
        credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)


    prompt = """ <instructions>
    You are an expert at adverse outcome pathways (AOP) and SQLite databases; you have familiarity with executing SQLite queries
    over the AOP database. Now, image you are someone without expertise in the AOP database. Your goal is to come up with {n} questions
    that a non-expert would have about the AOP database. Next, you should come up with a SQLite query on the AOP database to answer
    the user's question using information about the AOP database. </instructions>

    <example>
    Sample questions are as shown in: {examples}
    </example>

    <context>
    AOP database dictionary: {aop_dict}
    </context>

    <formatting>
    Output your answer only in the format of a python dictionary, where the dictionary key is the user question and the value of each
    key is the corresponding SQLite query. Only respond with the dictionary in correct python syntax such that it can be directly
    ran in code.
    </formatting>
    """

    chain = ChatPromptTemplate.from_template(prompt) | llm | StrOutputParser()

    response = chain.invoke({
        'aop_dict': AOP_Info,
        'examples': Queries,
        'n': n
    })

    return response

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
    



