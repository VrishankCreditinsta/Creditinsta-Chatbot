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

    return "company_question"