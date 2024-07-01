from fastapi import FastAPI,WebSocket, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from chatModel import modelo
from vectorstore_maker import get_pdf_split, text_to_vector,test_vector,get_text_splits,get_docx_splits,get_ppt_splits
import aiofiles
import os
from uuid import uuid4
from typing import List
import logging 
from chatModelv2 import modelov2

from voice_to_text import voice2text

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)
requests_logger = logging.getLogger("requests")
requests_logger.setLevel(logging.WARNING)
documento=[]

# configuracion logging

## FASTAPI SERVER
    
    # FUNCION ASINCRONICA PARA RESPONDER PARALELAMENTE A PREGUNTAS DE CLIENTES
async def respuesta_LLM(pregunta,connect_id):
    respuesta= await modelo.final_chain.ainvoke(
    {"input": pregunta},
    config={"configurable": {"session_id": connect_id}}
   )
    return respuesta['answer']

model= modelov2()
async def command_LLM(command):
     async for event in model.graph.astream({"messages": [("user", command)]}, 
                                                
                                               stream_mode="values"):
            
                print("Assistant:", event["messages"][-1].content)

v2t= voice2text()
def transcribe(filename):
    print("entrando a funcion")
   
    try:
# Usar el reconocedor de Google para transcribir el audio
        text = v2t.transcribe_audio_file(filename)
     
    except Exception as e:
        print(e)
    
    
    finally:
        os.remove(filename)
        return text



app = FastAPI()
@app.post("/command/")
async def voice2text(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="File not provided")

    try:
        filename = file.filename
        file_path = filename
        print("empezando carga de archivo")
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        print("archivo cargado")
        return JSONResponse(status_code=200, content={"message": "File uploaded successfully!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        transcription= transcribe(file_path)
        print(transcription)
        await command_LLM(transcription)


@app.get("/admin")
async def adminWindow():
    return FileResponse("indexAdmin.html")

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/archivos")
async def paginaCargaArchivos():
    return FileResponse("vectorUpdater.html")

@app.post("/upload")
async def extract_text_from_pdf(files: List[UploadFile] = File(...)):
    # Ensure the uploaded file is a PDF
    results=[]
    cantidad= len(files)
    current=1
    logger.info("     Empezando procesamiento de archivos")
    # print("Empezando procesamiento de archivos")
    for file in files:
        print(f"{file.filename} : Archivo {current}/{cantidad}")

        try:
                logger.info("     Archivo del tipo correcto, iniciando procesamiento ...")
                # print("Archivo del tipo correcto, iniciando procesamiento ...")
                # Read the PDF file contents
                contents = await file.read()
                

                # Save the PDF file temporarily
                async with aiofiles.open(file.filename, 'wb') as f:
                    await f.write(contents)
                    
                if file.content_type == 'application/pdf':

                    texto_splitted=get_pdf_split(file.filename)
                    

                    # Clean up (remove the temporary file)
                    os.remove(file.filename)
                    
                    text_to_vector(texto_splitted,"vectorstorev2")
                    
                    
                    
                elif file.content_type == 'text/plain':
                    texto_splitted=get_text_splits(file.filename)
                    text_to_vector(texto_splitted,"vectorstorev2")
                    
                    os.remove(file.filename)
                elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    
                    texto_splitted=get_docx_splits(file.filename)
                    
                    text_to_vector(texto_splitted,"vectorstorev2")
                    
                    #  test_vector("vectorstorev2","simulacion")
                    os.remove(file.filename)

                elif file.content_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                    
                    texto_splitted= get_ppt_splits(file.filename)
                    text_to_vector(texto_splitted,"vectorstorev2")
                    os.remove(file.filename)
                else:
                    logger.warning("      Este tipo de archivo no es compatible por el momento")
                    # print("Este tipo de archivo no es compatible por el momento")

                logger.info("   Archivo añadido al vectorstore")
                # print("Archivo añadido al vectorstore")
                current+=1


            
                results.append({'filename': file.filename, 'text': texto_splitted})



                

        except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'There was an error processing the file: {str(e)}'
                )

        finally:
                await file.close()
                
    return {'message': 'Files processed successfully', 'results': results}
    
@app.get("/upload")
async def show_files():
    return documento

# SE GUARDAN LAS CONEXIONES en un diccionario
ws_connections = {}
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # se crea un codigo unico por usuario, el cual es usado guardar el historial de chat 
    connection_id= str(uuid4())
    try:
        await websocket.accept()
        logger.info("     WebSocket connection accepted")
        # print("WebSocket connection accepted")
        ws_connections[connection_id] = websocket
        logger.info("     Connection ID: %s",connection_id)
        # print(f"Connection ID: {connection_id}")
        # print(ws_connections)
       
            # Handle the initial message from the client
        data = await websocket.receive_text()
        # print("Received initial message:", data)
        
            

            # Enter the loop to continuously receive and send messages
        while True:
            # print("Entering while loop")
            # SE RECIBE PREGUNTA
            data = await websocket.receive_text()
            logger.info("    %s",data)
            # SE CREA RESPUESTA ASINCRONICA
            
            
            respuesta= await respuesta_LLM(data,connection_id)
            
            
            await websocket.send_text(respuesta)
            logger.info("   %s",respuesta)
            # print(respuesta)
        

    except Exception as e:
        logger.error("  Error in Websocket handler: %s",e)
        # print(f"Error in WebSocket handler: {e}")
        # se elimina
        if connection_id in ws_connections:
            del ws_connections[connection_id]

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