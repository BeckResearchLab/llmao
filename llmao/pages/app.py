import streamlit as st
from langchain_.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.querying import AOP_query_chain
from utils.utils import Questions, AOP_Info, langfuse_handler
from utils.eval import Chat_Evaluator
from langchain_community.chat_models import BedrockChat
import random
from langfuse import Langfuse

langfuse = Langfuse()
langfuse.auth_check()

llm = BedrockChat(credentials_profile_name="default", model_id="anthropic.claude-3-sonnet-20240229-v1:0", verbose=True)
#llm = BedrockChat(credentials_profile_name="default", model_id="mistral.mixtral-8x7b-instruct-v0:1", verbose=True)

# page configuration
st.set_page_config(
    page_title='llmao',
    layout='wide',
    menu_items={
        'About': '#This is a header.'
    })

st.title('LLMao: AI-Toxicology Expert🧪🧬')

# initialize chat history
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

# first, classify the users question by topic
def route(human_question, chat_history):
    intro_prompt =  PromptTemplate.from_template(""" <instructions>
        Given the user question below, classify whether it has anything at all to do with the
        adverse outcome pathway (AOP) database or any of its tables, listed below. 
        If the question directly mentions the AOP database, any of its tables, or any of its columns, respond with database. Otherwise, respond with none.
        Do not respond with more than one word, and do not include punctuation or uppercase letters. </instructions>
                        
        <examples>
            Question: Describe the AOP gene table
            Your response: database
            Question: Can you tell me which molecules in the AOP database are the nastiest nasties of the bunch?
            Your response: database
        </example>

        <context> 
        AOP database schema dictionary: {aop_dict}
        User question: {question}
        </context>
        Classification:"""
    )
    
    route_chain = intro_prompt | llm | StrOutputParser()

    # path variable is database or none
    path = (route_chain.invoke({
        "question": human_question,
        "aop_dict": AOP_Info
    }, config={"callbacks":[langfuse_handler]}).lower())

    if chat_history is not None:
        Chat_Evaluator(human_question, chat_history)
    else:
        pass

    # if aop database is needed to answer the question
    if str(path) == 'database':
        # enter sql chain
        return AOP_query_chain(human_question, chat_history)
    # if a database is not needed to answer the question, answer normally
    else:
        # generic template
        template = """ <instructions>
        You are a friendly, cheerful, and helpful assistant. 
        Answer the following questions considering the chat history and user question.
        If the chat history is empty, do not mention the chat history </instructions>

        Chat history: {chat_history}
        question: {user_question}
        """

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser() 

        return chain.stream({
            "user_question": human_question, 
            "chat_history": chat_history
        })

def reset_conversation():
    '''
    reset the conversation history both visually and in llm memory
    '''
    st.session_state.conversation = None
    st.session_state.chat_history = []

def generate_question():
    '''
    generate a random question from question_bank in utils to ask the model
    '''

    i = random.randrange(0, len(Questions), 1)

    with st.chat_message("Human"):
        st.markdown(Questions[i])

    with st.chat_message("AI"):
        ai_response = st.write_stream(route(Questions[i], st.session_state.chat_history))
    
    return 


# reset button using the reset_conversation function
reset_button = st.button('Reset Chat 👈', on_click=reset_conversation)
generate_question = st.button('Generate Question✨', on_click=generate_question)

# chat box at the bottom of the page for user input
human_question = st.chat_input("Your message: ")

if human_question is not None and human_question != "":
    st.session_state.chat_history.append(HumanMessage(human_question))

    with st.chat_message("Human"):
        st.markdown(human_question)

    with st.chat_message("AI"):
        ai_response = st.write_stream(route(human_question, st.session_state.chat_history))
        st.write(ai_response)

    st.session_state.chat_history.append(AIMessage(content=ai_response))