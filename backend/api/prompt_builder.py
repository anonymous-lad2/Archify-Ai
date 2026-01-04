def build_architecture_prompt(topic: str, level: str, content: str) -> str:
    return f"""You are a senior software architect expert. Analyze the documentation and create a {level} architecture diagram.

CRITICAL RULES:
1. Return ONLY valid JSON - no markdown, no text before/after
2. Every component MUST have: type, shape, color, description
3. Every relationship MUST have: from, to, type, line, arrow
4. Component names must be EXACT same in relationships
5. Use 4-8 components for {level} level
6. Return empty arrays if you cannot determine valid data

VALID TYPES:
component type: client | gateway | microservice | database | cache | queue | external | infrastructure
line style: solid | dashed | dotted
relationship type: request | response | sync_call | async_event | read_write
shape: rounded_rectangle | circle | hexagon | rounded_square | cylinder | lightning | stack | shield

COLORS: Use hex like #4A90E2, #7B68EE, #50C878, #FF6B6B, #FFA500

EXAMPLE OUTPUT:
{{
  "components": {{
    "Web Client": {{"type": "client", "shape": "rounded_rectangle", "color": "#4A90E2", "description": "User interface"}},
    "Load Balancer": {{"type": "gateway", "shape": "hexagon", "color": "#7B68EE", "description": "Route traffic"}},
    "API Server": {{"type": "microservice", "shape": "rounded_square", "color": "#50C878", "description": "Process requests"}},
    "Database": {{"type": "database", "shape": "cylinder", "color": "#FF6B6B", "description": "Store data"}}
  }},
  "relationships": [
    {{"from": "Web Client", "to": "Load Balancer", "type": "request", "line": "solid", "arrow": true}},
    {{"from": "Load Balancer", "to": "API Server", "type": "sync_call", "line": "solid", "arrow": true}},
    {{"from": "API Server", "to": "Database", "type": "read_write", "line": "solid", "arrow": true}}
  ]
}}

DOCUMENTATION TO ANALYZE:
{content}

SYSTEM: {topic}
ARCHITECTURE LEVEL: {level}

Now generate the {level} architecture for {topic} based on the documentation above.
Return ONLY the JSON object, nothing else."""
