import time
from app.services.embeddings import model
from app.services.vector_store import collection
from app.services.llm import generate_production_answer
from app.router import analyze_intent_and_rewrite
from app.db import get_or_create_session, add_message, get_recent_messages

DISTANCE_THRESHOLD = 0.55  # Cosine distance cutoff (smaller is closer; >0.55 means irrelevant)

def chat(message: str, session_id: str = None, user_id: int = 1) -> dict:
    start_time = time.perf_counter()

    # 1. Ensure DB session
    session = get_or_create_session(session_id=session_id, user_id=user_id)
    active_session_id = session["session_id"]

    # 2. Add user message to DB
    add_message(active_session_id, sender="user", message=message, message_type="text")

    # 3. Retrieve recent history for context
    history = get_recent_messages(active_session_id, limit=6)
    preceding_history = history[:-1] if len(history) > 1 else []

    # 4. Production Intent Analysis & Query Rewriting
    analysis = analyze_intent_and_rewrite(message, history=preceding_history)
    intent = analysis.get("intent", "general_finance")
    rewritten_query = analysis.get("rewritten_query", message)
    is_dissatisfied = analysis.get("is_dissatisfied", False)

    # 5. Handle GREETING
    if intent == "greeting":
        greeting_msg = "Hello! I am Vabisor, your CreditInsta financial assistant. How can I help you manage your credit, loans, or investments today?"
        chips = ["Check Loan Eligibility", "What is CreditInsta?", "Improve CIBIL Score", "Mutual Funds Basics"]
        add_message(active_session_id, sender="bot", message=greeting_msg, message_type="greeting")
        return {
            "session_id": active_session_id,
            "type": "greeting",
            "message": greeting_msg,
            "suggested_chips": chips,
            "show_manager_connect": False,
            "rewritten_query": rewritten_query
        }

    # 6. Handle MANAGER REQUEST / HUMAN ESCALATION
    if intent == "manager_request" or "manager" in message.lower() or "human" in message.lower() or "support" in message.lower() and ("connect" in message.lower() or "talk" in message.lower() or "call" in message.lower()):
        manager_msg = "I understand. I can immediately connect you with our dedicated CredVisor Manager for personalized assistance."
        chips = ["Call CredVisor Support", "Request a Callback", "Continue Chatting with Bot"]
        add_message(active_session_id, sender="bot", message=manager_msg, message_type="manager_connect")
        return {
            "session_id": active_session_id,
            "type": "manager_connect",
            "message": manager_msg,
            "suggested_chips": chips,
            "show_manager_connect": True,
            "rewritten_query": rewritten_query
        }

    # 7. Handle OFF-TOPIC / JAILBREAK
    if intent == "off_topic":
        refusal_msg = "I am Vabisor, CreditInsta's financial assistant. I can only assist you with questions related to CreditInsta services and personal finance."
        chips = ["What services does CreditInsta offer?", "Personal Loan Inquiry", "CIBIL Score Tips"]
        add_message(active_session_id, sender="bot", message=refusal_msg, message_type="off_topic")
        return {
            "session_id": active_session_id,
            "type": "off_topic",
            "message": refusal_msg,
            "suggested_chips": chips,
            "show_manager_connect": False,
            "rewritten_query": rewritten_query
        }

    # 7. Knowledge Retrieval with strict relevance filtering
    context = ""
    if intent == "creditinsta_docs":
        query_emb = model.encode(rewritten_query, normalize_embeddings=True)
        results = collection.query(
            query_embeddings=[query_emb.tolist()],
            n_results=3
        )
        if results and "documents" in results and len(results["documents"]) > 0:
            docs = results["documents"][0]
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)
            
            # Filter only relevant docs by threshold
            valid_docs = [doc for doc, dist in zip(docs, distances) if dist <= DISTANCE_THRESHOLD]
            context = "\n\n".join(valid_docs)

    # 8. Context-Aware LLM Synthesis
    result = generate_production_answer(
        question=message,
        context=context,
        history=preceding_history,
        intent=intent
    )

    bot_reply = result.get("answer", "")
    chips = result.get("suggested_chips", ["Ask another question", "Connect with Manager"])

    # 9. Save bot reply to DB
    add_message(active_session_id, sender="bot", message=bot_reply, message_type="answer")

    # Manager Connect Trigger: If user is dissatisfied or explicit query fails
    show_manager = bool(is_dissatisfied or "connect to manager" in message.lower() or "call support" in message.lower())

    return {
        "session_id": active_session_id,
        "type": "answer",
        "message": bot_reply,
        "suggested_chips": chips,
        "show_manager_connect": show_manager,
        "rewritten_query": rewritten_query
    }
