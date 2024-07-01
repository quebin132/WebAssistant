from ast import Store
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
# Import necessary modules
import os
from dotenv import dotenv_values

store={}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

# Load environment variables from .env file
env_values = dotenv_values('.env')

# Get environment variables
openai_key = env_values['OPENAI_API_KEY']

class modelo:

         
    # se inicializa el modelo
    chat=ChatOpenAI(model="gpt-3.5-turbo-0125",temperature=0.2,api_key=openai_key)



    # Se crean los vectorstores FAISS y los retrievers

    embeddings=OpenAIEmbeddings(api_key=openai_key)

    vectorstore = FAISS.load_local("vectorstorev2",embeddings,allow_dangerous_deserialization="true")

    retriever=vectorstore.as_retriever()

    promptContextualizador= """Teniendo en cuenta el historial del chat y la ultima pregunta del usuario \
    la cual puede referenciar contexto del historial del chat, formula una nueva pregunta que pueda ser \
    entendida sin necesidad del historial del chat. NO respondas esta pregunta, simplemente \
    reformulala si es necesario o de lo contrario devuelvela sin cambios.
    """ 
    templateContextualizador= ChatPromptTemplate.from_messages(
        [
        ("system", promptContextualizador),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
    )

    history_aware_retriever = create_history_aware_retriever(
    chat, retriever,templateContextualizador
    )   
 


    # Se arma la cadena
    qaSystemPrompt= """ Eres un asistente virtual para Citylab Biobio.\
    Responde las preguntas de la mejor manera posible basandote en el contexto proporcionado. \
    Si no sabes la respuesta, di que no la sabes simplemente.\
    limita las respuestas a un maximo de 40 palabras.\
    
    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qaSystemPrompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
    )
    question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
  


    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    # parser=StrOutputParser()
    final_chain=conversational_rag_chain
    # prompt=ChatPromptTemplate.from_template(template)
    # 
    # setup_retrieval= RunnableParallel(
    #     {"context": retriever, "question":RunnablePassthrough()}
    # )

    # chain= setup_retrieval|prompt|chat|parser




