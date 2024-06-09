from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import fitz
import os
def get_pdf_split(path):
  print("entrando a funcion")
  textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                             chunk_overlap=15,
                                             length_function=len)
  document = fitz.open(path)
  print("archivo abierto dentro de funcion")
  text = ""
  for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
  print("extraccion de texto completada")
  document.close()  # Ensure the document is closed
  #Pages will be list of pages, so need to modify the loop
  
  textoSpliteado = textSplit.split_text(text)
  print("texto spliteado")
  
  return textoSpliteado

def get_text_splits(text_file):
  """Function takes in the text data and returns the  
  splits so for further processing can be done."""
  with open(text_file,'r') as txt:
    data = txt.read()

  textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                             chunk_overlap=15,
                                             length_function=len)
  doc_list = textSplit.split_text(data)
  return doc_list

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


def text_to_vector(doc_list,vector_path):
    if os.path.exists(vector_path):
      tempVector= FAISS.load_local(vector_path,OpenAIEmbeddings(),allow_dangerous_deserialization="true")
      vectorAdd =FAISS.from_texts(doc_list,OpenAIEmbeddings())
      tempVector.merge_from(vectorAdd)
      tempVector.save_local(vector_path)
    else:
      vectorAdd =FAISS.from_texts(doc_list,OpenAIEmbeddings())
      vectorAdd.save_local(vector_path)
        

def test_vector(vector_path,query):
    vector=FAISS.load_local(vector_path,OpenAIEmbeddings(),allow_dangerous_deserialization="true")
    vector.similarity_search(query)
# Se crean los vectorstores FAISS y los retrievers


# vectorstore = FAISS.load_local("vectorstore_assistant_alfa")
# vectorstore.save_local("vectorstore_assistant_alfa")