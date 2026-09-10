from app.ingestion.documents import load_all_documents
from app.ingestion.chunking import split_document
from app.services.embeddings import embedding
from app.services.vector_store import add_documents
from app.ingestion.faq import fetch_faqs, convert_faqs_to_documents



def ingest_documents():

    print("Loading documents...")

    docs = load_all_documents()

    print(f"Documents loaded: {len(docs)}")


    print("Fetching FAQs...")

    faqs = fetch_faqs()

    faq_documents = convert_faqs_to_documents(faqs)

    print(f"FAQs converted: {len(faq_documents)}")


    docs.extend(faq_documents)

    print(f"Total documents: {len(docs)}")


    print("Creating chunks...")

    chunks = split_document(docs)

    print(f"Chunks created: {len(chunks)}")


    print("Creating embeddings...")

    embeddings = embedding(chunks)


    print("Storing in ChromaDB...")

    add_documents(chunks, embeddings)


    print("Ingestion completed.")


if __name__ == "__main__":
    ingest_documents()