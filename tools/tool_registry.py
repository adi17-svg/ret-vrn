# """
# tool_registry.py

# - Central registry for all tools
# - NO GPT calls
# - NO Firestore
# - Only rules / configuration
# """

# from typing import Dict, Optional

# # ======================================================
# # TOOL REGISTRY
# # ======================================================
# # Each tool defines:
# # - id
# # - response_type
# # - allow_questions
# # - allow_actions
# # - description

# TOOL_REGISTRY: Dict[str, Dict] = {}


# # ======================================================
# # REGISTER HELPER
# # ======================================================
# def register_tool(tool: Dict):
#     """
#     Register a tool safely.
#     """
#     tool_id = tool.get("id")
#     if not tool_id:
#         raise ValueError("Tool must have an id")

#     TOOL_REGISTRY[tool_id] = tool


# def get_tool(tool_id: Optional[str]) -> Optional[Dict]:
#     """
#     Fetch tool config by id
#     """
#     if not tool_id:
#         return None

#     return TOOL_REGISTRY.get(tool_id)
"""
tool_registry.py

- Central registry for all tools
- NO GPT calls
- NO Firestore
- Only rules / configuration
"""

from typing import Dict, Optional

# ======================================================
# TOOL REGISTRY
# ======================================================
# Each tool defines:
# - id
# - response_type
# - allow_questions
# - allow_actions
# - description

TOOL_REGISTRY: Dict[str, Dict] = {}


# ======================================================
# REGISTER HELPER
# ======================================================
def register_tool(tool: Dict):
    """
    Register a tool safely.
    """
    tool_id = tool.get("id")
    if not tool_id:
        raise ValueError("Tool must have an id")

    TOOL_REGISTRY[tool_id] = tool


def get_tool(tool_id: Optional[str]) -> Optional[Dict]:
    """
    Fetch tool config by id
    """
    if not tool_id:
        return None

    return TOOL_REGISTRY.get(tool_id)


# ======================================================
# TOOL DECLARATIONS (ADD ALL TOOLS HERE)
# ======================================================

# 🔹 Getting Going with Action
register_tool({
    "id": "getting_going",
    "response_type": "listen",   # tone locked
    "allow_questions": False,    # no reflective questions
    "allow_actions": False,      # no missions / spiral actions
    "description": "Helps user get unstuck and take a tiny action"
})

# 🔹 Gratitude Tool
register_tool({
    "id": "gratitude",
    "response_type": "listen",
    "allow_questions": True,
    "allow_actions": False,
    "description": "Guided gratitude reflection"
})

# 🔹 Breathing Tool
register_tool({
    "id": "breathing",
    "response_type": "listen",
    "allow_questions": False,
    "allow_actions": False,
    "description": "Simple breathing exercise to calm the user"
})

# 🔹 Reflection Tool
register_tool({
    "id": "reflection",
    "response_type": "reflect",
    "allow_questions": True,
    "allow_actions": False,
    "description": "Guided self-reflection"
})

# 👉 पुढे 100+ tools असतील तर
# इथे फक्त असेच register_tool({...}) add करत जा
