import hashlib
import chromadb


client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="creditinsta_knowledge")


'''if "creditinsta_knowledge" in [c.name for c in client.list_collections()]:
    client.delete_collection("creditinsta_knowledge")'''

collection = client.get_or_create_collection(
    name="creditinsta_knowledge"
)



def generate_document_id(document, index):

    source = document.metadata.get("source", "unknown")

    if source == "faq_api":
        faq_id = document.metadata.get("faq_id")
        return f"faq_{faq_id}_{index}"

    content_hash = hashlib.md5(
        document.page_content.encode("utf-8")
    ).hexdigest()

    return f"{source}_{index}_{content_hash}"


def add_documents(chunks, embeddings):

    ids = [
        generate_document_id(chunk, index)
        for index, chunk in enumerate(chunks)
    ]

    documents = [
        chunk.page_content
        for chunk in chunks
    ]

    metadatas = [
        chunk.metadata
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print(f"Upserted {len(chunks)} chunks into ChromaDB")


def delete_faq(faq_id):
    collection.delete(
        where={
            "source": "faq_api",
            "faq_id": str(faq_id)
        }
    )
    print(f"Deleted FAQ {faq_id} from ChromaDB")



if __name__ == "__main__":

    print("Collection:", collection.name)
    print("Number of documents:", collection.count())