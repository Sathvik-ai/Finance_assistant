from fastapi import FastAPI, Query
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

app = FastAPI()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = FAISS.load_local("index/news_index", embeddings, allow_dangerous_deserialization=True)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})

@app.get("/retrieve")
def retrieve_chunks(query: str = Query(...), company: str = Query(None)):
    search_query = f"{query} {company}" if company else query
    results = retriever.get_relevant_documents(search_query)
    return {"results": [doc.page_content for doc in results]}
