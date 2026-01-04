import json
import re
from backend.utils.llm_client import call_llm
from backend.api.prompt_builder import build_architecture_prompt


def extract_json_from_response(response: str) -> dict:
    """
    Extract JSON from LLM response, handling markdown code blocks and extra text.
    """
    try:
        # Try direct parsing first
        return json.loads(response)
    except:
        pass
    
    # Try to extract JSON from markdown code blocks
    try:
        # Look for ```json ... ``` or ``` ... ```
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except:
        pass
    
    # Try to find any JSON object in the response
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
    except:
        pass
    
    return None


def get_fallback_architecture(topic: str, level: str) -> dict:
    """
    Provide a basic fallback architecture when LLM fails or content is empty.
    """
    base_components = {
        "Client": {
            "type": "client",
            "shape": "rounded_rectangle",
            "color": "#4A90E2",
            "description": "User interface"
        },
        "API Gateway": {
            "type": "gateway",
            "shape": "hexagon",
            "color": "#7B68EE",
            "description": "Request router"
        },
        "Core Service": {
            "type": "microservice",
            "shape": "rounded_square",
            "color": "#50C878",
            "description": f"{topic} service"
        },
        "Database": {
            "type": "database",
            "shape": "cylinder",
            "color": "#FF6B6B",
            "description": "Data storage"
        }
    }
    
    base_relationships = [
        {
            "from": "Client",
            "to": "API Gateway",
            "type": "request",
            "line": "solid",
            "arrow": True
        },
        {
            "from": "API Gateway",
            "to": "Core Service",
            "type": "sync_call",
            "line": "solid",
            "arrow": True
        },
        {
            "from": "Core Service",
            "to": "Database",
            "type": "read_write",
            "line": "solid",
            "arrow": True
        }
    ]
    
    return {
        "components": base_components,
        "relationships": base_relationships
    }


def generate_architecture(topic: str, level: str, raw_content: str) -> dict:
    """
    Generate architecture from scraped content using LLM.
    Falls back to basic architecture if content is empty or LLM fails.
    """
    
    # Check if we have meaningful content
    if not raw_content or len(raw_content.strip()) < 100:
        print(f"⚠️ Insufficient content ({len(raw_content) if raw_content else 0} chars). Using fallback architecture.")
        return get_fallback_architecture(topic, level)
    
    print(f"🤖 Generating architecture with {len(raw_content)} chars of content...")
    
    try:
        prompt = build_architecture_prompt(topic, level, raw_content)
        response = call_llm(prompt)
        
        print(f"📋 LLM Response length: {len(response)} chars")
        
        # Try to extract JSON from response
        architecture = extract_json_from_response(response)
        
        if architecture and architecture.get("components") and architecture.get("relationships"):
            print(f"✅ Generated {len(architecture.get('components', {}))} components and {len(architecture.get('relationships', []))} relationships")
            return architecture
        else:
            print("⚠️ LLM returned invalid JSON structure. Using fallback.")
            return get_fallback_architecture(topic, level)
            
    except Exception as e:
        print(f"❌ Error generating architecture: {e}")
        return get_fallback_architecture(topic, level)
