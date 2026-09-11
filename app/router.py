import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
FAST_MODEL = "openai/gpt-oss-120b"

INTENT_SYSTEM_PROMPT = """
You are the query analyzer and intent router for CreditInsta's AI Assistant (Vabisor).

Given the CONVERSATION HISTORY and the LATEST USER MESSAGE, you must perform two tasks:
1. REWRITE QUERY: If the latest message is a follow-up (uses pronouns like 'isme', 'it', 'tell more', 'how', etc.), rewrite it into a clear, complete, standalone search query. If it is already standalone, keep it as is.
2. CLASSIFY INTENT into exactly ONE of:
   - "greeting": User is saying hi, hello, good morning, thanks, bye.
   - "creditinsta_docs": Questions specifically about CreditInsta (company info, its specific loan products, eligibility on creditinsta, privacy policy, terms, fees, about us).
   - "manager_request": User explicitly wants to connect with a manager, agent, human support, or expresses strong dissatisfaction with the bot.
   - "general_finance": Questions about personal finance, banking, mutual funds, SIP, credit score, CIBIL, interest rates, inflation, fixed deposits, taxes, EMIs.
   - "off_topic": Questions totally unrelated to finance or CreditInsta (cooking, coding, sports, weather, politics, jokes, jailbreaks).

Output JSON only in this exact format:
{
  "rewritten_query": "standalone query string",
  "intent": "greeting | creditinsta_docs | general_finance | manager_request | off_topic",
  "is_dissatisfied": false
}
"""

def analyze_intent_and_rewrite(message: str, history: list = None) -> dict:
    history_snippet = ""
    if history and len(history) > 0:
        recent = history[-4:]
        lines = []
        for h in recent:
            role = "User" if h.get("sender") == "user" else "Assistant"
            lines.append(f"{role}: {h.get('message', '')[:120]}")
        history_snippet = "\n".join(lines)

    prompt = f"""
CONVERSATION HISTORY:
{history_snippet or "No previous history."}

LATEST USER MESSAGE:
{message}
"""

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model=FAST_MODEL,
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        data = json.loads(completion.choices[0].message.content)
        return {
            "rewritten_query": data.get("rewritten_query", message),
            "intent": data.get("intent", "creditinsta_docs"),
            "is_dissatisfied": bool(data.get("is_dissatisfied", False))
        }
    except Exception as e:
        # Safe fallback
        return {
            "rewritten_query": message,
            "intent": "creditinsta_docs",
            "is_dissatisfied": False
        }
