import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
import requests
from tqdm import tqdm
import time



########################################
#### Setup variables                ####     
########################################

# Model path 
model_path = "llama-2-7b-chat.Q4_K_M.gguf"

if not os.path.exists(model_path):
    print(f"Downloading {model_path}...")
    # You may want to replace the model URL by another of your choice
    model_url = "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf"
    response = requests.get(model_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(model_path, 'wb') as f:
        for data in tqdm(response.iter_content(chunk_size=1024), total=total_size//1024):
            f.write(data)
    print("[System] Download complete!")
else:
    print("[System] Model already exists! Proceeding...")