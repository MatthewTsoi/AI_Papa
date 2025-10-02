import os, time 

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp

import project_init

########################################
#### Setup variables                ####     
########################################
src_doc="docs"
src_vectorDB="chroma_dbs"

os.makedirs(src_doc, exist_ok=True)
os.makedirs(src_vectorDB, exist_ok=True)

def loadtext2Chunks(test_mode=True):

    if test_mode:
        print("[system] test mode activated in {loadtext2Vector}")

    if test_mode:
        # Sample text for demonstration purposes
        with open(src_doc+"/sample.txt", "w") as f:
            f.write("""
            Retrieval-Augmented Generation (RAG) is a technique that combines retrieval-based and generation-based approaches
            for natural language processing tasks. It involves retrieving relevant information from a knowledge base and then 
            using that information to generate more accurate and informed responses.
            
            RAG models first retrieve documents that are relevant to a given query, then use these documents as additional context
            for language generation. This approach helps to ground the model's responses in factual information and reduces hallucinations.
            
            The llama.cpp library is a C/C++ implementation of Meta's LLaMA model, optimized for CPU usage. It allows running LLaMA models
            on consumer hardware without requiring high-end GPUs.
            
            LocalAI is a framework that enables running AI models locally without relying on cloud services. It provides APIs compatible
            with OpenAI's interfaces, allowing developers to use their own models with the same code they would use for OpenAI services.
            """)

    documents = []
    for file in os.listdir(src_doc):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(src_doc, file))
            documents.extend(loader.load())
        elif file.endswith(".txt"):
            loader = TextLoader(os.path.join(src_doc, file))
            documents.extend(loader.load())
 
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
 
    chunks = text_splitter.split_documents(documents)

    ########################################
    #### Test text segments into chunks ####     
    ########################################
    if test_mode:
        print(len(chunks))

        for chunk in chunks[0:]:
            print(chunk)
            print()         
            
    return chunks


def initVectorStore(i_chunks):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(
    documents=i_chunks,
    embedding=embeddings,
    persist_directory="./"+src_vectorDB
    )

    return vectorstore  

def setupQA_template():
    template = """
    Answer the question based on the following context:
    
    {context}

    Question: {question}
    Answer:
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    return prompt 

def setupQA_template_V2():
    template = """
    You are a digital assistant in eMPF office, provide guidence to users. 
    Answer the question based on the following context. If any uncertain information, ask to contact MPFA for further advise. 
    
    {context}

    Question: {question}
    Answer:
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    return prompt 

def ask_question(question, i_pipeline):
    start_time = time.time()
    result = i_pipeline.invoke({"query": question})
    end_time = time.time()
    
    print(f"Question: {question}")
    print(f"Answer: {result['result']}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print("\nSource documents:")
    for i, doc in enumerate(result["source_documents"]):
        print(f"Document {i+1}:")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Content: {doc.page_content[:200]}...\n")


if __name__ == '__main__':
    vectorstore= initVectorStore(loadtext2Chunks(test_mode=False))
    print("[System] RAG vector store completed.")

    llm = LlamaCpp(
        model_path=project_init.model_path,
        temperature=0.7,
        max_tokens=2000,
        n_ctx=4096,
        n_batch = 64, 
        n_gpu_layers = -1 ,
        verbose=True
    )

    rag_pipeline = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        #verbose=True, 
        #chain_type_kwargs={"verbose": True, "prompt": setupQA_template()}
        chain_type_kwargs={"prompt": setupQA_template_V2()}
    )

    # Testing set 
    ask_question("How much does it cost when I apply for the eMPF platform access", rag_pipeline)
    #ask_question("Who should apply for empf platform", rag_pipeline)
    #ask_question("what can I do on the empf platform")

    llm.client.close() 
    print("[System] Process shutdown completed.")
