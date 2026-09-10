from sentence_transformers import SentenceTransformer

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

