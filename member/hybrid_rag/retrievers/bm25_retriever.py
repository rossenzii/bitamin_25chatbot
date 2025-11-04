from langchain_community.retrievers import BM25Retriever

def get_bm25_retriever(vectorstore):
    docs = list(vectorstore.docstore._dict.values())
    bm25_retriever = BM25Retriever.from_documents(docs)
    return bm25_retriever