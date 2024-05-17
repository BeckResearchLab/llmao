from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import BedrockChat
from utils.utils import AOP_Info, Queries
import pandas as pd
import numpy as np
from numpy.linalg import norm
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from typing import Union

def Generator(n: int = 10, k: int=5, return_list: bool=True) -> Union[list[list], pd.DataFrame]:
    '''
    generate AOP questions, AI answers, and context
    args
        n - number of question:query pairs to output, default 5
        k - # of results used for SQLite LIMIT statement, default 5
        return_list - use false to return pd dataframe object
    returns
        data - dictionary {question:query} or 
            pandas dataframe, column 1 is the question and column 2 is the SQLite query
    '''
    from utils.querying import AOP_query_chain

    generate_prompt = """ <instructions>
    You are an expert at adverse outcome pathways (AOP) and SQLite databases; you have familiarity with executing SQLite queries
    over the AOP database. Your goal is to come up with questions that a user might have about how the AOP database works, what it's purpose is,
    and how to understand some of the complex data inside of it. Come up with a question according to the user's
    skill level shown in the context, based on the schema of the AOP database. Your goal is solely to come up with 1 question,
    and try to make it unique from the current questions shown in the context. </instructions>

    <example>
    Sample questions are as shown in: {examples}
    </example>

    <context>
    Skill-level: {skill_level}
    AOP database schema dictionary: {aop_dict}
    Current questions: {current_questions}
    </context>

    <formatting>
    Output only the question based on the above context and instructions. Do not output any content other than
    the question you are responding with.
    </formatting>
    """

    llm = BedrockChat(
            credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)
    
    chain = ChatPromptTemplate.from_template(generate_prompt) | llm | StrOutputParser()

    skill_level= ["No AOP knowledge","Beginner level AOP knowledge", "Intermediate level AOP knowledge", "Expert level AOP knowledge"]

    questions = []
    contexts = []
    responses = []

    for i in range(0, n):
        question = chain.invoke({
            'aop_dict': AOP_Info,
            'examples': Queries,
            'skill_level': skill_level[i % len(skill_level)],
            'top_k': k,
            'current_questions': questions
        })
        response, context = AOP_query_chain(question=question, chat_history="",stream=False)
        questions.append(question)
        responses.append(response)
        contexts.append(context)

    # return list of lists by default
    result = []
    for i in range(0, len(questions)):
        result.append([questions[i], responses[i], contexts[i]])
    if return_list:
        return result
    # return dataframe
    else:
        return pd.DataFrame(result, columns=["Question", "AI_Response", "Context"])

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

def cos_similarity(embedding_list: list):
    '''
    perform cosine similarity calculation between two vectors (lists)
    '''
    embedding_model = BedrockEmbeddings(credentials_profile_name='default', model_id="amazon.titan-embed-text-v1")
    embedding1, embedding2 = embedding_model.embed_documents(embedding_list)
    return np.dot(embedding1, embedding2)/(norm(embedding1)*norm(embedding2))

def f1_score(var_list: list):
    '''
    args
        var list must be [True Positives, False Positives, False Negatives]
    '''
    TP, FP, FN = var_list
    return TP / (np.abs(TP) + (0.5*(np.abs(FP)) + np.abs(FN)))

