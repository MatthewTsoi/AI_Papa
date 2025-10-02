# AI_Papa
Repo for my journey of AI &amp; robotics 

## What's NEW?

### 20191031 Adding [ER waiting time predictor] (xxx) - a quick demo of predicting waiting time on HK public hospital emergeny room using public open data 
### 20190916 Adding [facelook](facelook_photo_management)- a simple photo / face management using AWS face recognition (free up-to 5000 photos requests every month)
### 20201123 Adding simple web dasbboard from twitter data streams. 
### 20251002 Adding [Local LLM] project, demostrating a build of local LLM with RAG for a simple bot


#### Local LLM
This commit ("initial RAG build") adds the first implementation of a Retrieval-Augmented Generation (RAG) pipeline using LangChain and LlamaCpp. It introduces the main script RAG_run.py, which loads documents (PDF and TXT), splits them into chunks, creates a Chroma vector store with HuggingFace embeddings, and sets up a QA chain using a custom prompt template. The script demonstrates asking a sample question about eMPF platform costs. Supporting files added include a project initialization script (project_init.py), requirements, setup commands, and sample documents (eMPF_FAQ.txt, sample.txt). The commit establishes the basic structure for local RAG-based QA using Llama-2 and ChromaDB.
