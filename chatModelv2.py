from typing import Optional, Type
import requests
from rapidfuzz import process,fuzz
from langchain.pydantic_v1 import BaseModel,Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
import os
from dotenv import dotenv_values
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

import asyncio



class fetchMapInput(BaseModel):
    mapa : str = Field(description="Tipo de mapa que se quiere pedir")

class InputPlacas(BaseModel):
    placa : str = Field(description="Placa que se quiere cambiar, debe ser un numero")

class FetchMapTool(BaseTool):
    name = "Mapas"
    description = "Necesaria para desplegar mapas de Citylab"
    args_schema: Type[BaseModel] = fetchMapInput
    return_direct: bool = True

    def _run(
        self, mapa: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Usa la herramienta"""
        mapa_min = mapa.lower()

        url_get= "http://192.168.31.120:8500//api/set_map_type/"
        map_to_code = {
            "diversidad de Suelo" : 1,
            "educacion" : 2,
            "proximidad de cultura": 3, 
            "poblacion" : 4,
            "parques" : 6,
            "plazas" : 7,
            "aprovisionamiento" : 8,
            "comercio" : 9,
            "edificacion" : 10,
            "salud" : 11
        

        }
        mapa_final= process.extractOne(mapa_min,map_to_code.keys())[0]
    
        url_get += '?map_type=' + str(map_to_code[mapa_final]);
        try:
            requests.get(url=url_get)
        finally:

            return url_get

    async def _arun(
        self,
        mapa: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        # If the calculation is cheap, you can just delegate to the sync implementation
        # as shown below.
        # If the sync calculation is expensive, you should delete the entire _arun method.
        # LangChain will automatically provide a better implementation that will
        # kick off the task in a thread to make sure it doesn't block other async code.
        return self._run(mapa, run_manager=run_manager.get_sync())
    

    
class CambiarPlaca(BaseTool):
    name = "Placas"
    description = "Cambio de placas en mapas Citylab"
    args_schema: Type[BaseModel] = InputPlacas
    return_direct: bool = True

    state= [13,14,15,16,17,18,19]
    def _run(
        self, placa: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        url_get= "http://192.168.31.120:8500/api/set_map_state/"
        try:
            placa_int = int(placa)
        finally:
            if fuzz.ratio(placa,"estado default")> 50:
                default_state=[13,14,15,16,17,18,19]
                new_state = ",".join(map(str, default_state))
            elif placa_int not in [1,2,3,4,5,6,7]:
                return "Lo siento, repita el comando por favor"

                
            else:   

                placa_n= placa_int + 12
                
                for n in range(len(self.state)):
                    if (self.state[n]==placa_n or self.state[n]==(placa_n+7)):
                        if(self.state[n] >=20):
                            self.state[n] -=7
                        else:
                            self.state[n] +=7
                new_state = ",".join(map(str, self.state))
            url_get += "?slots=" + new_state
        try:
            requests.get(url=url_get)
            print(new_state)
            print(url_get)
        finally:

            return f"placa {placa} cambiada con exito"
   
        


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]



class modelov2:

    def __init__(self):
        self.env_values = dotenv_values('.env')
        self.openai_key = self.env_values['OPENAI_API_KEY']
        self.tool_map= FetchMapTool()
        self.tool_placa= CambiarPlaca()
        self.herramientas= [self.tool_map,self.tool_placa]
        self.llm = ChatOpenAI(model="gpt-3.5-turbo",api_key=self.openai_key)
        self.llm_with_tools=self.llm.bind_tools(self.herramientas)
        self.graph_builder = StateGraph(State)
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.tool_node= ToolNode(tools=self.herramientas)
        self.graph_builder.add_node("tools", self.tool_node)
        self.graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        )
        self.graph_builder.add_edge("tools","chatbot")
        self.graph_builder.set_entry_point("chatbot")

        self.graph = self.graph_builder.compile()
    # Get environment variables
      
    async def chatbot(self,state: State):
        messages = state["messages"]
        response = await self.llm_with_tools.ainvoke(messages)
        return {"messages": [response]}


    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
   
    # memory = AsyncSqliteSaver.from_conn_string(":memory:")
    

# user_input = "User: quiero ver el mapa de educacion"
# config = {"configurable": {"thread_id": "1"}}
# from langchain_core.messages import HumanMessage

# config = {"configurable": {"thread_id": "1"}}

# model= modelov2()

# async def main():
#     while True:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break
#         async for event in model.graph.astream({"messages": [("user", user_input)]}, config, stream_mode="values"):
            
#                 print("Assistant:", event["messages"][-1].content)

# asyncio.run(main())


            
           

