# # """
# # tool_registry.py

# # - Central registry for all tools
# # - NO GPT calls
# # - NO Firestore
# # - Only rules / configuration
# # """

# # from typing import Dict, Optional

# # # ======================================================
# # # TOOL REGISTRY
# # # ======================================================
# # # Each tool defines:
# # # - id
# # # - response_type
# # # - allow_questions
# # # - allow_actions
# # # - description

# # TOOL_REGISTRY: Dict[str, Dict] = {}


# # # ======================================================
# # # REGISTER HELPER
# # # ======================================================
# # def register_tool(tool: Dict):
# #     """
# #     Register a tool safely.
# #     """
# #     tool_id = tool.get("id")
# #     if not tool_id:
# #         raise ValueError("Tool must have an id")

# #     TOOL_REGISTRY[tool_id] = tool


# # def get_tool(tool_id: Optional[str]) -> Optional[Dict]:
# #     """
# #     Fetch tool config by id
# #     """
# #     if not tool_id:
# #         return None

# #     return TOOL_REGISTRY.get(tool_id)
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


# # ======================================================
# # TOOL DECLARATIONS (ADD ALL TOOLS HERE)
# # ======================================================

# # 🔹 Getting Going with Action
# register_tool({
#     "id": "getting_going",
#     "response_type": "listen",   # tone locked
#     "allow_questions": False,    # no reflective questions
#     "allow_actions": False,      # no missions / spiral actions
#     "description": "Helps user get unstuck and take a tiny action"
# })

# # 🔹 Gratitude Tool
# register_tool({
#     "id": "gratitude",
#     "response_type": "listen",
#     "allow_questions": True,
#     "allow_actions": False,
#     "description": "Guided gratitude reflection"
# })

# # 🔹 Breathing Tool
# register_tool({
#     "id": "breathing",
#     "response_type": "listen",
#     "allow_questions": False,
#     "allow_actions": False,
#     "description": "Simple breathing exercise to calm the user"
# })

# # 🔹 Reflection Tool
# register_tool({
#     "id": "reflection",
#     "response_type": "reflect",
#     "allow_questions": True,
#     "allow_actions": False,
#     "description": "Guided self-reflection"
# })
# register_tool({
#     "id": "self_compassion",
#     "response_type": "listen",
#     "allow_questions": False,
#     "allow_actions": False,
#     "description": "Gentle self-kindness when feeling low"
# })

# # 👉 पुढे 100+ tools असतील तर
# # इथे फक्त असेच register_tool({...}) add करत जा
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
# LOW MOOD TOOLS (ALL 15 – INCLUDING GETTING GOING)
# ======================================================

LOW_MOOD_TOOLS = [
    # Activation
    {
        "id": "getting_going",
        "description": "Helps user get unstuck and take a tiny action",
    },

    # Self regulation
    {
        "id": "self_compassion",
        "description": "Gentle self-kindness when feeling low",
    },
    {
        "id": "grounding_54321",
        "description": "Grounding exercise to return to the present moment",
    },
    {
        "id": "breath_word",
        "description": "Simple breath with word anchor to calm the nervous system",
    },

    # Emotional release / validation
    {
        "id": "venting",
        "description": "Let emotions out without fixing or judging",
    },
    {
        "id": "it_makes_sense",
        "description": "Validates emotional reactions without analysis",
    },
    {
        "id": "name_the_feeling",
        "description": "Name the emotion without explaining or judging it",
    },

    # Body & safety
    {
        "id": "body_checkin",
        "description": "Quick body awareness to release tension",
    },
    {
        "id": "one_safe_thing",
        "description": "Anchor attention to a sense of safety",
    },

    # Cognitive load reduction
    {
        "id": "lower_the_bar",
        "description": "Reduce expectations on low-energy days",
    },
    {
        "id": "thought_parking",
        "description": "Set aside heavy thoughts temporarily",
    },
    {
        "id": "no_decision_now",
        "description": "Release pressure to decide immediately",
    },

    # Energy & pacing
    {
        "id": "today_is_heavy",
        "description": "Permission to slow down on heavy days",
    },
    {
        "id": "tiny_relief",
        "description": "Find and stay with even 1% relief",
    },
    {
        "id": "gentle_distraction",
        "description": "Short neutral distraction to break loops",
    },
]

# ======================================================
# REGISTER ALL LOW MOOD TOOLS
# ======================================================

for tool in LOW_MOOD_TOOLS:
    register_tool({
        "id": tool["id"],
        "response_type": "listen",     # tone locked
        "allow_questions": False,      # no reflective questions
        "allow_actions": False,        # no missions / spiral actions
        "description": tool["description"],
    })

# ======================================================
# OTHER NON–LOW MOOD TOOLS (KEEP AS IS)
# ======================================================

# 🔹 Gratitude Tool
register_tool({
    "id": "gratitude",
    "response_type": "listen",
    "allow_questions": True,
    "allow_actions": False,
    "description": "Guided gratitude reflection"
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
# फक्त LOW_MOOD_TOOLS सारखे blocks add करत जा
