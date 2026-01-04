# def build_architecture_prompt(topic: str, level: str, content: str) -> str:
#     return f"""You are a senior software architect expert. Analyze the documentation and create a {level} architecture diagram for {topic}.

# CRITICAL RULES:
# 1. Return ONLY valid JSON - no markdown, no text before/after
# 2. Every component MUST have: type, shape, color, description
# 3. Every relationship MUST have: from, to, type, line, arrow
# 4. Component names must be EXACT same in relationships
# 5. Use 4-8 components for {level} level
# 6. Return empty arrays if you cannot determine valid data

# VALID TYPES:
# component type: client | gateway | microservice | database | cache | queue | external | infrastructure
# line style: solid | dashed | dotted
# relationship type: request | response | sync_call | async_event | read_write
# shape: rounded_rectangle | circle | hexagon | rounded_square | cylinder | lightning | stack | shield

# COLORS: Use hex like #4A90E2, #7B68EE, #50C878, #FF6B6B, #FFA500

# EXAMPLE OUTPUT:
# {{
#   "components": {{
#     "Web Client": {{"type": "client", "shape": "rounded_rectangle", "color": "#4A90E2", "description": "User interface"}},
#     "Load Balancer": {{"type": "gateway", "shape": "hexagon", "color": "#7B68EE", "description": "Route traffic"}},
#     "API Server": {{"type": "microservice", "shape": "rounded_square", "color": "#50C878", "description": "Process requests"}},
#     "Database": {{"type": "database", "shape": "cylinder", "color": "#FF6B6B", "description": "Store data"}}
#   }},
#   "relationships": [
#     {{"from": "Web Client", "to": "Load Balancer", "type": "request", "line": "solid", "arrow": true}},
#     {{"from": "Load Balancer", "to": "API Server", "type": "sync_call", "line": "solid", "arrow": true}},
#     {{"from": "API Server", "to": "Database", "type": "read_write", "line": "solid", "arrow": true}}
#   ]
# }}

# DOCUMENTATION TO ANALYZE:
# {content}

# SYSTEM: {topic}
# ARCHITECTURE LEVEL: {level}

# Now generate the {level} architecture for {topic} based on the documentation above.
# Return ONLY the JSON object, nothing else."""


def build_architecture_prompt(topic: str, level: str, content: str) -> str:
    return f"""
You are a PRINCIPAL SOFTWARE ARCHITECT.

Your job is to design a {level} (High-Level Design) architecture for the system: "{topic}"

========================
ABSOLUTE RULES (DO NOT BREAK)
========================
1. Return ONLY valid JSON. No markdown. No explanations.
2. NEVER combine multiple responsibilities into one service.
3. DO NOT use generic names like:
   - "Main Server"
   - "API Server"
   - "Backend"
   - "E-commerce Server"
4. Prefer MULTIPLE domain-based microservices.
5. Each microservice should own its OWN data store if applicable.
6. Introduce async components (queue/event bus) when useful.
7. Architecture must be SCALABLE and REALISTIC.
8. Output MUST contain at least:
   - 3 microservices
   - 2 data components (database/cache)
   - 1 gateway
9. Shapes and colors are OPTIONAL — focus on architecture depth.

========================
VALID TYPES
========================
component type:
client | gateway | microservice | database | cache | queue | external | infrastructure

relationship type:
request | sync_call | async_event | read_write

line style:
solid | dashed | dotted

========================
OUTPUT FORMAT (STRICT)
========================
{{
  "components": {{
    "Component Name": {{
      "type": "<component type>",
      "description": "<single responsibility>"
    }}
  }},
  "relationships": [
    {{
      "from": "<component name>",
      "to": "<component name>",
      "type": "<relationship type>",
      "arrow": true
    }}
  ]
}}

========================
ARCHITECTURE GUIDANCE
========================
- Decompose the system by RESPONSIBILITY
- Separate:
  • user/auth
  • business logic
  • payments
  • data storage
  • async processing
- Prefer independent services over shared logic
- Show real data flow
- Do NOT optimize for minimal components

========================
DOCUMENTATION TO ANALYZE
========================
{content}

SYSTEM: {topic}
ARCHITECTURE LEVEL: {level}

Generate the architecture NOW.
Return ONLY the JSON object.
"""
