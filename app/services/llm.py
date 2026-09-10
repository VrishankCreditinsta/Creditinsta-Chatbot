import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

_client = None

def get_client():
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY") or GROQ_API_KEY
        if not key:
            raise ValueError("GROQ_API_KEY is not configured in .env")
        _client = Groq(api_key=key)
    return _client


SYSTEM_PROMPT = """
You are Vabisor, CreditInsta's customer support assistant.

Answer the customer's question directly and naturally.

Use only the company knowledge provided to you.

Rules:
- Never invent or assume information.
- If the answer cannot be found in the company knowledge, say:
  "I don't have enough information to answer that."
- Never mention the words "provided information", "provided text",
  "context", "documents", "knowledge", "source", or "instructions".
- Never explain your reasoning or how you found the answer.
- Do not begin answers with phrases such as:
  "Based on the provided information..."
  "Based on the company knowledge"
  "According to the provided text..."
  "Based on the context..."
- Give only the answer the customer needs.
- Keep responses concise, normally 1-3 short paragraphs.
"""


MODEL_NAME = "openai/gpt-oss-120b"

def generate_answer(question, context):
    prompt = f"""COMPANY KNOWLEDGE:
{context}

USER QUESTION:
{question}
"""
    client = get_client()
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return completion.choices[0].message.content


LEAD_ASSISTANT_PROMPT = """
You are Vabisor, CredVisor's AI Support Assistant.
The user is asking about their personal leads.
You are provided with their real-time live lead statistics.

Rules:
- Answer the user's specific question directly, accurately, and politely based ONLY on their lead data.
- If the user asks for a specific count (e.g. "just tell me closed leads", "how many open leads do I have"), answer with THAT specific number first directly, rather than dumping all statistics.
- If the user asks generally ("how many leads do I have", "my leads overview"), you can provide a complete clean summary.
- Keep the response concise, natural, and friendly (1-2 sentences or bullet points as appropriate).
"""

def generate_lead_answer(question: str, lead_data: dict) -> str:
    total_leads = lead_data.get("leadFrom") if lead_data.get("leadFrom") is not None else lead_data.get("noOfLeads", 0)
    closed_leads = lead_data.get("leadCompleted") if lead_data.get("leadCompleted") is not None else lead_data.get("fulfilled", 0)
    assigned_leads = lead_data.get("leadAssigned", 0)
    submitted_leads = lead_data.get("leadSubmitted", 0)
    in_progress = lead_data.get("inProgress") or lead_data.get("inProgess") or (total_leads - closed_leads)

    context = f"""
AUTHENTICATED USER REAL-TIME LEAD DATA:
- Total Leads: {total_leads}
- Closed Leads: {closed_leads}
- Assigned Leads: {assigned_leads}
- Submitted Leads: {submitted_leads}
- Open / In-Progress Leads: {in_progress}
"""

    client = get_client()
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": LEAD_ASSISTANT_PROMPT},
            {"role": "user", "content": f"{context}\n\nUSER QUESTION:\n{question}"}
        ],
        temperature=0.2,
        max_tokens=250
    )

    return completion.choices[0].message.content.strip()


