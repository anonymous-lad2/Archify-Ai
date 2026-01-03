from backend.utils.llm_client import call_llm

def extract_topic(query: str) -> str:
    prompt = f"""
        Extract the main software system or architecture topic.
        Return ONLY 1-3 words.
        No explanation.

        Input:
        {query}
    """
    
    topic = call_llm(prompt)
    return topic