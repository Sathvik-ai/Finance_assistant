from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def build_vector_store(doc_path: str, index_path: str):
    loader = TextLoader(doc_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(split_docs, embeddings)
    vectordb.save_local(index_path)
    print(f"✅ Vector store saved at: {index_path}")

if __name__ == "__main__":
    build_vector_store("data/news.txt", "index/news_index")
