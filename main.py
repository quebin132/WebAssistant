from fastapi import FastAPI,WebSocket, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from chatModel import modelo
from vectorstore_maker import get_pdf_split, text_to_vector,test_vector
import aiofiles
import os
documento=[]


## FASTAPI SERVER
    
    # FUNCION ASINCRONICA PARA RESPONDER PARALELAMENTE A PREGUNTAS DE CLIENTES
async def respuesta_LLM(pregunta):
   await modelo.chain.ainvoke(pregunta)



app = FastAPI()


@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/archivos")
async def paginaCargaArchivos():
    return FileResponse("vectorUpdater.html")

@app.post("/upload")
async def extract_text_from_pdf(file: UploadFile = File(...)):
    # Ensure the uploaded file is a PDF
    print("entrando a upload")
    if file.content_type == 'application/pdf':
       

        try:
            # Read the PDF file contents
            contents = await file.read()
            print("se leyo el archivo")

            # Save the PDF file temporarily
            async with aiofiles.open(file.filename, 'wb') as f:
                await f.write(contents)
                print("se guardo el archivo")

            texto_splitted=get_pdf_split(file.filename)
            print("se spliteo el archivo")

            # Clean up (remove the temporary file)
            os.remove(file.filename)
            print("se elimino el archivo")
            text_to_vector(texto_splitted,"vectorstore_prueba")
            print("vector guardado")
            test_vector("vectorstore_prueba","modelo")
            print("vector testeado")



            return {'message': f'Successfully uploaded {file.filename}', 'text': texto_splitted}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'There was an error processing the file: {str(e)}'
            )

        finally:
            await file.close()
    
@app.get("/upload")
async def show_files():
    return documento
# SE GUARDAN LAS CONEXIONES
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
            print("Entering while loop")
            # SE RECIBE PREGUNTA
            data = await websocket.receive_text()
            print( data)
            # SE CREA RESPUESTA ASINCRONICA
            respuesta= await modelo.chain.ainvoke(data)
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