from sentence_transformers import SentenceTransformer
from app.ingestion.documents import load_all_documents
from app.ingestion.chunking import split_document

MODEL_NAME="BAAI/bge-base-en-v1.5"

model=SentenceTransformer(MODEL_NAME)

def embedding(chunks):
    text=[chunk.page_content for chunk in chunks]

    embeddings=model.encode(
        text,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    return embeddings

