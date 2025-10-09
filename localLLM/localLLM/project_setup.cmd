REM setup python virtual environment
python -m venv localLLM 
cd localLLM 
.\Scripts\activate.bat


REM install required python lin
pip install llama-cpp-python
pip install langchain langchain-community sentence-transformers chromadb
pip install pypdf requests pydantic tqdm
pip install -U langchain-huggingface
pip install -U langchain-community
