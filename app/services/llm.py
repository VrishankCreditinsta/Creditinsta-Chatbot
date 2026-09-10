import os 

from  dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

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

MODEL_NAME="gemini-3.6-flash"

def generate_answer(question, context):

    prompt = f"""
    COMPANY KNOWLEDGE:
    {context}

    USER QUESTION:
    {question}
    """

    response = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
        system_instruction=SYSTEM_PROMPT
    )

    return response.output_text


''''if __name__ == "__main__":
    question = "What is CreditInsta?"
    
    context = """
    CreditInsta is a financial services company that provides
    credit-related services to customers.
    """

    answer = generate_answer(question, context)

    print("\nQuestion:", question)
    print("\nAnswer:", answer)'''

import time

'''if __name__ == "__main__":


    question = "What is 2 + 2?"

    context = "Basic arithmetic: 2 + 2 = 4."

    start_time = time.perf_counter()

    answer = generate_answer(question, context)

    elapsed = time.perf_counter() - start_time

    print("\nAnswer:", answer)
    print(f"\nLLM latency: {elapsed:.2f} seconds") '''