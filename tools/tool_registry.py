
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
# # LOW MOOD TOOLS (ALL 15 – INCLUDING GETTING GOING)
# # ======================================================

# LOW_MOOD_TOOLS = [
#     # Activation
#     {
#         "id": "getting_going",
#         "description": "Helps user get unstuck and take a tiny action",
#     },

#     # Self regulation
#     {
#         "id": "self_compassion",
#         "description": "Gentle self-kindness when feeling low",
#     },
#     {
#         "id": "grounding_54321",
#         "description": "Grounding exercise to return to the present moment",
#     },
#     {
#         "id": "breath_word",
#         "description": "Simple breath with word anchor to calm the nervous system",
#     },

#     # Emotional release / validation
#     {
#         "id": "venting",
#         "description": "Let emotions out without fixing or judging",
#     },
#     {
#         "id": "it_makes_sense",
#         "description": "Validates emotional reactions without analysis",
#     },
#     {
#         "id": "name_the_feeling",
#         "description": "Name the emotion without explaining or judging it",
#     },

#     # Body & safety
#     {
#         "id": "body_checkin",
#         "description": "Quick body awareness to release tension",
#     },
#     {
#         "id": "one_safe_thing",
#         "description": "Anchor attention to a sense of safety",
#     },

#     # Cognitive load reduction
#     {
#         "id": "lower_the_bar",
#         "description": "Reduce expectations on low-energy days",
#     },
#     {
#         "id": "thought_parking",
#         "description": "Set aside heavy thoughts temporarily",
#     },
#     {
#         "id": "no_decision_now",
#         "description": "Release pressure to decide immediately",
#     },

#     # Energy & pacing
#     {
#         "id": "today_is_heavy",
#         "description": "Permission to slow down on heavy days",
#     },
#     {
#         "id": "tiny_relief",
#         "description": "Find and stay with even 1% relief",
#     },
#     {
#         "id": "gentle_distraction",
#         "description": "Short neutral distraction to break loops",
#     },
# ]

# # ======================================================
# # REGISTER ALL LOW MOOD TOOLS
# # ======================================================

# for tool in LOW_MOOD_TOOLS:
#     register_tool({
#         "id": tool["id"],
#         "response_type": "listen",     # tone locked
#         "allow_questions": False,      # no reflective questions
#         "allow_actions": False,        # no missions / spiral actions
#         "description": tool["description"],
#     })

# # ======================================================
# # OTHER NON–LOW MOOD TOOLS (KEEP AS IS)
# # ======================================================

# # 🔹 Gratitude Tool
# register_tool({
#     "id": "gratitude",
#     "response_type": "listen",
#     "allow_questions": True,
#     "allow_actions": False,
#     "description": "Guided gratitude reflection"
# })

# # 🔹 Reflection Tool
# register_tool({
#     "id": "reflection",
#     "response_type": "reflect",
#     "allow_questions": True,
#     "allow_actions": False,
#     "description": "Guided self-reflection"
# })

# # 👉 पुढे 100+ tools असतील तर
# # फक्त LOW_MOOD_TOOLS सारखे blocks add करत जा
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
# LOW MOOD TOOLS (15)
# ======================================================

LOW_MOOD_TOOLS = [
    # Activation
    {"id": "getting_going", "description": "Helps user get unstuck and take a tiny action"},

    # Self regulation
    {"id": "self_compassion", "description": "Gentle self-kindness when feeling low"},
    {"id": "grounding_54321", "description": "Grounding exercise to return to the present moment"},
    {"id": "breath_word", "description": "Breath with word anchor to calm the nervous system"},

    # Emotional validation
    {"id": "venting", "description": "Let emotions out without fixing or judging"},
    {"id": "it_makes_sense", "description": "Validate feelings without analysis"},
    {"id": "name_the_feeling", "description": "Name the emotion without judging"},

    # Body & safety
    {"id": "body_checkin", "description": "Quick body awareness to release tension"},
    {"id": "one_safe_thing", "description": "Anchor attention to something safe"},

    # Cognitive load reduction
    {"id": "lower_the_bar", "description": "Reduce expectations on low-energy days"},
    {"id": "thought_parking", "description": "Temporarily park heavy thoughts"},
    {"id": "no_decision_now", "description": "Release pressure to decide immediately"},

    # Energy & pacing
    {"id": "today_is_heavy", "description": "Permission to slow down"},
    {"id": "tiny_relief", "description": "Stay with even 1% relief"},
    {"id": "gentle_distraction", "description": "Short neutral distraction"},
]

for tool in LOW_MOOD_TOOLS:
    register_tool({
        "id": tool["id"],
        "response_type": "listen",
        "allow_questions": False,
        "allow_actions": False,
        "description": tool["description"],
    })

# ======================================================
# ANXIETY TOOLS (10)
# ======================================================

ANXIETY_TOOLS = [
    {"id": "anxiety_breath_478", "description": "4-7-8 breathing to calm anxiety"},
    {"id": "anxiety_exhale_focus", "description": "Longer exhale to calm the nervous system"},
    {"id": "anxiety_grounding_touch", "description": "Use physical touch to feel grounded"},

    {"id": "anxiety_you_are_safe", "description": "Gentle reassurance of present safety"},
    {"id": "anxiety_this_will_pass", "description": "Reminder that anxiety states pass"},
    {"id": "anxiety_body_not_danger", "description": "Anxiety sensations are not dangerous"},

    {"id": "anxiety_name_the_fear", "description": "Name the fear without fixing it"},
    {"id": "anxiety_not_now", "description": "Contain worries for later"},

    {"id": "anxiety_slow_down", "description": "Permission to slow down"},
    {"id": "anxiety_soft_focus", "description": "Gentle visual focus to reduce hypervigilance"},
]

for tool in ANXIETY_TOOLS:
    register_tool({
        "id": tool["id"],
        "response_type": "listen",
        "allow_questions": False,
        "allow_actions": False,
        "description": tool["description"],
    })

# ======================================================
# OTHER NON–LOW MOOD / NON–ANXIETY TOOLS
# ======================================================
# ======================================================
# SLEEP TOOLS
# ======================================================

SLEEP_TOOLS = [
    {"id": "body_shutdown_cue", "description": "Body wind-down before sleep"},
    {"id": "cant_sleep_acceptance", "description": "Normalize being awake at night"},
    {"id": "late_night_overthinking", "description": "Soften late-night thinking"},
    {"id": "mind_unload", "description": "Unload thoughts before sleep"},
    {"id": "nighttime_safety_anchor", "description": "Reassure safety at night"},
    {"id": "emotional_day_wind_down", "description": "Close emotional day gently"},
    {"id": "irregular_sleep_reset", "description": "Rebalance sleep rhythm"},
    {"id": "morning_damage_control", "description": "Reduce morning anxiety after poor sleep"},
    {"id": "phone_detachment_bridge", "description": "Gently detach from phone before sleep"},
    {"id": "sleep_after_conflict", "description": "Calm body after argument before sleep"},
    {"id": "sleep_guilt_release", "description": "Release guilt around sleep struggles"},
    {"id": "sleep_identity_repair", "description": "Rebuild confidence around sleep"},
]

for tool in SLEEP_TOOLS:
    register_tool({
        "id": tool["id"],
        "response_type": "listen",
        "allow_questions": False,
        "allow_actions": False,
        "description": tool["description"],
    })

# ======================================================
# RELATIONSHIP TOOLS
# ======================================================

RELATIONSHIP_TOOLS = [
    {"id": "attachment_activation_check", "description": "Detect attachment panic or clinginess"},
    {"id": "conflict_hangover_release", "description": "Release emotional residue after conflict"},
    {"id": "people_pleasing_interrupt", "description": "Interrupt automatic yes pattern"},
    {"id": "silent_expectations_detector", "description": "Detect unspoken expectations"},
    {"id": "emotional_distance_repair", "description": "Soften emotional detachment"},
    {"id": "trust_vs_fear_clarifier", "description": "Differentiate trust from fear"},
    {"id": "over_giving_recovery", "description": "Recover after over-giving"},
    {"id": "resentment_drain", "description": "Release stored resentment"},
    {"id": "communication_freeze_breaker", "description": "Unblock stuck communication"},
    {"id": "post_argument_regulation", "description": "Settle nervous system after argument"},
    {"id": "emotional_dependency_soften", "description": "Balance emotional dependency"},
    {"id": "relationship_reality_check", "description": "Reality vs fantasy differentiation"},
    {"id": "boundaries_in_love_tool", "description": "Maintain identity in love"},
    {"id": "let_go_without_cutting_off", "description": "Detach calmly without drama"},
]

for tool in RELATIONSHIP_TOOLS:
    register_tool({
        "id": tool["id"],
        "response_type": "reflect",
        "allow_questions": True,
        "allow_actions": False,
        "description": tool["description"],
    })

# Gratitude Tool
register_tool({
    "id": "gratitude",
    "response_type": "listen",
    "allow_questions": True,
    "allow_actions": False,
    "description": "Guided gratitude reflection",
})

# Reflection Tool
register_tool({
    "id": "reflection",
    "response_type": "reflect",
    "allow_questions": True,
    "allow_actions": False,
    "description": "Guided self-reflection",
})

# ======================================================
# NOTES
# ======================================================
# - Add future tools by creating a list like LOW_MOOD_TOOLS
# - Then loop + register_tool
# - routes.py remains untouched
# - Tool behavior lives ONLY inside tools/<category>/*
