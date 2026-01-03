def extract_topic(query: str) -> str:
    q = query.lower()

    if "ecommerce" in q or "e-commerce" in q:
        return "E-commerce System"
    if "chat" in q:
        return "Chat Application"
    if "payment" in q:
        return "Payment System"

    return "Software System"
