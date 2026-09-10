def classify_message(message):
    message = message.lower().strip()

    greetings = [
        "hi",
        "hii",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    if message in greetings:
        return "greeting"

    lead_keywords = [
        "lead",
        "leads",
        "open lead",
        "open leads",
        "meri lead",
        "meri kitni lead",
        "kitne lead",
        "kitni leads",
        "lead status",
        "assigned lead",
        "submitted lead"
    ]

    for kw in lead_keywords:
        if kw in message:
            return "lead_inquiry"

    return "company_question"