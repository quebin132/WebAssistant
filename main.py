from fastapi import FastAPI,WebSocket
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import requests
##### INTENTAR PONER CHATMODEL ACA
# se inicializa el modelo
chat=ChatOpenAI(model="gpt-3.5-turbo-0125")



# Se crean los vectorstores FAISS y los retrievers

embeddings=OpenAIEmbeddings()

vectorstore = FAISS.load_local("vectorstore_assistant_alfa",embeddings,allow_dangerous_deserialization="true")

retriever=vectorstore.as_retriever()



# Se arma la cadena
template= """ responde la pregunta basandote en el siguiente contexto:
{context}

pregunta: {question}

"""
prompt=ChatPromptTemplate.from_template(template)
parser=  StrOutputParser()
setup_retrieval= RunnableParallel(
    {"context": retriever, "question":RunnablePassthrough()}
)

chain= setup_retrieval|prompt|chat|parser

## FASTAPI SERVER

class Respuesta(BaseModel):
    respuesta : str
    
class Pregunta(BaseModel):
    pregunta: str
    



app = FastAPI()

@app.get("/")
async def home():
    return FileResponse("pruebachat.html")

# respuestaChat=""
# @app.post("/respuestas/")
# async def respuestaToPagina(item:Respuesta):
#     print("llego la respuesta")
#     respuestaChat=item

#     print(item)
#     return item

# @app.post("/preguntas/")
# async def preguntas_store(item:Pregunta):
#     print("llego pregunta")
#     return item

# @app.get("/respuestas/")
# async def respuestaToPagina(item:Respuesta):
#     print("extrayendo pregunta")
#     print(item)
#     return respuestaChat

# @app.get("/preguntas/")
# async def preguntas_store(item:Pregunta):
#     print("llego pregunta")
#     return item
   

ws_connections = set()
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        print("WebSocket connection accepted")
        ws_connections.add(websocket)

        # Handle the initial message from the client
        data = await websocket.receive_text()
        print("Received initial message:", data)
       
        

        # Enter the loop to continuously receive and send messages
        while True:
            print("Entering loop")
            data = await websocket.receive_text()
            print( data)
            respuesta=chain.invoke(data)
            await websocket.send_text(respuesta)
            print(respuesta)

    except Exception as e:
        print(f"Error in WebSocket handler: {e}")
        # Optionally, remove the WebSocket connection from the set
        ws_connections.remove(websocket)

# si no se monta este directorio no carga el javascript ni el css
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)



# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=10250)