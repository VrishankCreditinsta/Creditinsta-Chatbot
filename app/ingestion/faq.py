import requests
import os
from langchain_core.documents import Document


FAQ_API_URL = os.getenc("FAQ_API_URL")

if not FAQ_API_URL:
    raise ValueError("FAQ_API_URL is not configured")







def fetch_faqs():

    response = requests.get(
        FAQ_API_URL,
        headers={"Accept": "application/json"}
    )

    response.raise_for_status()

    return response.json()


def convert_faqs_to_documents(faqs):

    documents = []

    for faq in faqs:

        if faq.get("deleted") is True:
            continue

        question = faq.get("question", "").strip()
        answer = faq.get("answer", "").strip()

        if not question or not answer:
            continue

        document = Document(
            page_content=f"Question: {question}\nAnswer: {answer}",
            metadata={
                "source": "faq_api",
                "faq_id": str(faq.get("id"))
            }
        )

        documents.append(document)

    return documents


if __name__ == "__main__":

    faqs = fetch_faqs()

    print("FAQs received:", len(faqs))

    print("\nFirst raw FAQ:")
    print(faqs[0])

    documents = convert_faqs_to_documents(faqs)

    print("Documents created:", len(documents))

    print("\nFirst FAQ:")
    print(documents[0])