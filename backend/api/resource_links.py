from backend.utils.llm_client import call_llm

def get_resource_links(topic: str, level: str) -> list[str]:
    prompt = f"""
        Give 5-7 authoritative documentation or blog links
        to learn {level} architecture of {topic}.
        Return ONLY URLs, one per line.
        No extra text.
    """
    response = call_llm(prompt)
    links = [line.strip() for line in response.split("\n") if line.strip().startswith("http")]
    return links