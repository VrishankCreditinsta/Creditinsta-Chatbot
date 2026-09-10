from app.services.embeddings import model
from app.services.vector_store import collection
from app.services.llm import generate_answer
import time
from app.router import classify_message



def chat(message):
    message_type = classify_message(message)

    if message_type == "greeting":
        return {
            "type": "greeting",
            "message": "Hi! I'm Vabisor, your customer support assistant. How can I help you today?"
        }

    answer = answer_question(message)

    return {
        "type": "answer",
        "message": answer
    }



def answer_question(question):

    start = time.time()

    question_embedding = model.encode(
        question,
        normalize_embeddings=True
    )

    '''print(f"Embedding time: {time.time() - start:.2f}s")'''

    retrieval_start = time.time()

    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=3
    )

    #print(f"Retrieval time: {time.time() - retrieval_start:.2f}s")

    documents = results["documents"][0]
    context = "\n\n".join(documents)

    llm_start = time.time()

    answer = generate_answer(question, context)

    #print(f"LLM time: {time.time() - llm_start:.2f}s")

    return answer

if __name__ == "__main__":

    question = "What happens if i miss an emi?"

    start_time = time.perf_counter()

    # 1. Create question embedding
    embedding_start = time.perf_counter()

    question_embedding = model.encode(
        question,
        normalize_embeddings=True
    )

    embedding_time = time.perf_counter() - embedding_start

    # 2. Retrieve from ChromaDB
    retrieval_start = time.perf_counter()

    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=3
    )

    retrieval_time = time.perf_counter() - retrieval_start

    # 3. Create context
    documents = results["documents"][0]
    context = "\n\n".join(documents)

    # 4. Generate answer using Gemini
    llm_start = time.perf_counter()

    answer = generate_answer(question, context)

    llm_time = time.perf_counter() - llm_start

    total_time = time.perf_counter() - start_time

    # 5. Display results
    print("\n==============================")
    print("RAG LATENCY TEST")
    print("==============================")

    print(f"\nEmbedding time : {embedding_time:.2f} seconds")
    print(f"Retrieval time : {retrieval_time:.2f} seconds")
    print(f"LLM time       : {llm_time:.2f} seconds")
    print(f"Total time     : {total_time:.2f} seconds")
    print("\nAnswer characters:", len(answer))

    print("\n==============================")
    print("QUESTION")
    print("==============================")
    

    print(question)

    print("\n==============================")
    print("ANSWER")
    print("==============================")

    print(answer)