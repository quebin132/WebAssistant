from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

class modelo:
    # se inicializa el modelo
    chat=ChatOpenAI(model="gpt-3.5-turbo-0125")



    # Se crean los vectorstores FAISS y los retrievers

    embeddings=OpenAIEmbeddings()

    vectorstore = FAISS.load_local("vectorstore_assistant_alfa",embeddings,allow_dangerous_deserialization="true")

    retriever=vectorstore.as_retriever()



    # Se arma la cadena
    template= """ responde la pregunta basandote en el siguiente contexto en menos de 40 palabras:
    {context}

    pregunta: {question}

    """
    prompt=ChatPromptTemplate.from_template(template)
    parser=  StrOutputParser()
    setup_retrieval= RunnableParallel(
        {"context": retriever, "question":RunnablePassthrough()}
    )

    chain= setup_retrieval|prompt|chat|parser