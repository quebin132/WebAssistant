from fastapi import FastAPI,WebSocket
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from chatModel import modelo




## FASTAPI SERVER
    
    # FUNCION ASINCRONICA PARA RESPONDER PARALELAMENTE A PREGUNTAS DE CLIENTES
async def respuesta_LLM(pregunta):
   await modelo.chain.ainvoke(pregunta)



app = FastAPI()

@app.get("/")
async def home():
    return FileResponse("index.html")

   
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