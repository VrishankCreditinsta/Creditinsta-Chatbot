from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.ingestion.documents import load_all_documents

docs=load_all_documents()


def split_document(doc):
    splitter=RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=100)

    chunks=splitter.split_documents(doc)

    return chunks

split=split_document(docs)
