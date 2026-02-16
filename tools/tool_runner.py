# # backend/tools/tool_runner.py

# def run_tool(tool_id: str):
#     """
#     Central dispatcher for all tools.
#     All tools follow the same contract:
#         def handle(step: str | None)

#     For v1, we ALWAYS call handle(None)
#     (opening state of the tool)
#     """

#     # ====================
#     # LOW MOOD TOOLS
#     # ====================
#     if tool_id == "getting_going":
#         from tools.low_mood.getting_going import handle
#         return handle(None)

#     if tool_id == "self_compassion":
#         from tools.low_mood.self_compassion import handle
#         return handle(None)

#     if tool_id == "grounding_54321":
#         from tools.low_mood.grounding_54321 import handle
#         return handle(None)

#     if tool_id == "breath_word":
#         from tools.low_mood.breath_word import handle
#         return handle(None)

#     if tool_id == "venting":
#         from tools.low_mood.venting import handle
#         return handle(None)

#     if tool_id == "it_makes_sense":
#         from tools.low_mood.it_makes_sense import handle
#         return handle(None)

#     if tool_id == "name_the_feeling":
#         from tools.low_mood.name_the_feeling import handle
#         return handle(None)

#     if tool_id == "body_checkin":
#         from tools.low_mood.body_checkin import handle
#         return handle(None)

#     if tool_id == "one_safe_thing":
#         from tools.low_mood.one_safe_thing import handle
#         return handle(None)

#     if tool_id == "lower_the_bar":
#         from tools.low_mood.lower_the_bar import handle
#         return handle(None)

#     if tool_id == "thought_parking":
#         from tools.low_mood.thought_parking import handle
#         return handle(None)

#     if tool_id == "no_decision_now":
#         from tools.low_mood.no_decision_now import handle
#         return handle(None)

#     if tool_id == "today_is_heavy":
#         from tools.low_mood.today_is_heavy import handle
#         return handle(None)

#     if tool_id == "tiny_relief":
#         from tools.low_mood.tiny_relief import handle
#         return handle(None)

#     if tool_id == "gentle_distraction":
#         from tools.low_mood.gentle_distraction import handle
#         return handle(None)

#     # ====================
#     # ANXIETY TOOLS
#     # ====================
#     if tool_id == "anxiety_breath_478":
#         from tools.anxiety.anxiety_breath_478 import handle
#         return handle(None)

#     if tool_id == "anxiety_exhale_focus":
#         from tools.anxiety.anxiety_exhale_focus import handle
#         return handle(None)

#     if tool_id == "anxiety_grounding_touch":
#         from tools.anxiety.anxiety_grounding_touch import handle
#         return handle(None)

#     if tool_id == "anxiety_you_are_safe":
#         from tools.anxiety.anxiety_you_are_safe import handle
#         return handle(None)

#     if tool_id == "anxiety_this_will_pass":
#         from tools.anxiety.anxiety_this_will_pass import handle
#         return handle(None)

#     if tool_id == "anxiety_body_not_danger":
#         from tools.anxiety.anxiety_body_not_danger import handle
#         return handle(None)

#     if tool_id == "anxiety_name_the_fear":
#         from tools.anxiety.anxiety_name_the_fear import handle
#         return handle(None)

#     if tool_id == "anxiety_not_now":
#         from tools.anxiety.anxiety_not_now import handle
#         return handle(None)

#     if tool_id == "anxiety_slow_down":
#         from tools.anxiety.anxiety_slow_down import handle
#         return handle(None)

#     if tool_id == "anxiety_soft_focus":
#         from tools.anxiety.anxiety_soft_focus import handle
#         return handle(None)

#     # ====================
#     # FALLBACK
#     # ====================
#     return None
# backend/tools/tool_runner.py
"""
Central dispatcher for all tools.

Design:
- NO GPT
- NO Firestore
- Stateless dispatcher
- Tool itself controls flow via `step`

Each tool MUST expose:
    def handle(step: str | None, user_text: str | None)

Frontend / API MUST pass:
- tool_id
- tool_step (can be None on first call)
- user text
"""


def run_tool(
    tool_id: str,
    step: str | None = None,
    user_text: str | None = None,
):
    """
    Dispatch tool execution.

    tool_id   → which tool
    step      → current step in tool flow
    user_text → whatever user typed (used only for framing)
    """

    # ====================
    # LOW MOOD TOOLS
    # ====================
    if tool_id == "getting_going":
        from tools.low_mood.getting_going import handle
        return handle(step, user_text)

    if tool_id == "self_compassion":
        from tools.low_mood.self_compassion import handle
        return handle(step, user_text)

    if tool_id == "grounding_54321":
        from tools.low_mood.grounding_54321 import handle
        return handle(step, user_text)

    if tool_id == "breath_word":
        from tools.low_mood.breath_word import handle
        return handle(step, user_text)

    if tool_id == "venting":
        from tools.low_mood.venting import handle
        return handle(step, user_text)

    if tool_id == "it_makes_sense":
        from tools.low_mood.it_makes_sense import handle
        return handle(step, user_text)

    if tool_id == "name_the_feeling":
        from tools.low_mood.name_the_feeling import handle
        return handle(step, user_text)

    if tool_id == "body_checkin":
        from tools.low_mood.body_checkin import handle
        return handle(step, user_text)

    if tool_id == "one_safe_thing":
        from tools.low_mood.one_safe_thing import handle
        return handle(step, user_text)

    if tool_id == "lower_the_bar":
        from tools.low_mood.lower_the_bar import handle
        return handle(step, user_text)

    if tool_id == "thought_parking":
        from tools.low_mood.thought_parking import handle
        return handle(step, user_text)

    if tool_id == "no_decision_now":
        from tools.low_mood.no_decision_now import handle
        return handle(step, user_text)

    if tool_id == "today_is_heavy":
        from tools.low_mood.today_is_heavy import handle
        return handle(step, user_text)

    if tool_id == "tiny_relief":
        from tools.low_mood.tiny_relief import handle
        return handle(step, user_text)

    if tool_id == "gentle_distraction":
        from tools.low_mood.gentle_distraction import handle
        return handle(step, user_text)

    # ====================
    # ANXIETY TOOLS
    # ====================
    if tool_id == "anxiety_breath_478":
        from tools.anxiety.anxiety_breath_478 import handle
        return handle(step, user_text)

    if tool_id == "anxiety_exhale_focus":
        from tools.anxiety.anxiety_exhale_focus import handle
        return handle(step, user_text)

    if tool_id == "anxiety_grounding_touch":
        from tools.anxiety.anxiety_grounding_touch import handle
        return handle(step, user_text)

    if tool_id == "anxiety_you_are_safe":
        from tools.anxiety.anxiety_you_are_safe import handle
        return handle(step, user_text)

    if tool_id == "anxiety_this_will_pass":
        from tools.anxiety.anxiety_this_will_pass import handle
        return handle(step, user_text)

    if tool_id == "anxiety_body_not_danger":
        from tools.anxiety.anxiety_body_not_danger import handle
        return handle(step, user_text)

    if tool_id == "anxiety_name_the_fear":
        from tools.anxiety.anxiety_name_the_fear import handle
        return handle(step, user_text)

    if tool_id == "anxiety_not_now":
        from tools.anxiety.anxiety_not_now import handle
        return handle(step, user_text)

    if tool_id == "anxiety_slow_down":
        from tools.anxiety.anxiety_slow_down import handle
        return handle(step, user_text)

    if tool_id == "anxiety_soft_focus":
        from tools.anxiety.anxiety_soft_focus import handle
        return handle(step, user_text)

    # ====================
    # SLEEP TOOLS
    # ====================
    if tool_id == "body_shutdown_cue":
        from tools.sleep.body_shutdown_cue import handle
        return handle(step, user_text)

    if tool_id == "cant_sleep_acceptance":
        from tools.sleep.cant_sleep_acceptance_tool import handle
        return handle(step, user_text)

    if tool_id == "late_night_overthinking":
        from tools.sleep.late_night_overthinking_softener import handle
        return handle(step, user_text)

    if tool_id == "mind_unload":
        from tools.sleep.mind_unload_before_sleep import handle
        return handle(step, user_text)

    if tool_id == "nighttime_safety_anchor":
        from tools.sleep.nighttime_safety_anchor import handle
        return handle(step, user_text)

    if tool_id == "emotional_day_wind_down":
        from tools.sleep.emotional_day_wind_down import handle
        return handle(step, user_text)

    if tool_id == "irregular_sleep_reset":
        from tools.sleep.irregular_sleep_reset import handle
        return handle(step, user_text)

    if tool_id == "morning_damage_control":
        from tools.sleep.morning_damage_control import handle
        return handle(step, user_text)

    if tool_id == "phone_detachment_bridge":
        from tools.sleep.phone_detachment_bridge import handle
        return handle(step, user_text)

    if tool_id == "sleep_after_conflict":
        from tools.sleep.sleep_after_conflict import handle
        return handle(step, user_text)

    if tool_id == "sleep_guilt_release":
        from tools.sleep.sleep_guilt_release import handle
        return handle(step, user_text)

    if tool_id == "sleep_identity_repair":
        from tools.sleep.sleep_identity_repair import handle
        return handle(step, user_text)
    # ====================
    # RELATIONSHIP TOOLS
    # ====================
    if tool_id == "attachment_activation_check":
        from tools.relationship.attachment_activation_check import handle
        return handle(step, user_text)

    if tool_id == "conflict_hangover_release":
        from tools.relationship.conflict_hangover_release import handle
        return handle(step, user_text)

    if tool_id == "people_pleasing_interrupt":
        from tools.relationship.people_pleasing_interrupt import handle
        return handle(step, user_text)

    if tool_id == "silent_expectations_detector":
        from tools.relationship.silent_expectations_detector import handle
        return handle(step, user_text)

    if tool_id == "emotional_distance_repair":
        from tools.relationship.emotional_distance_repair import handle
        return handle(step, user_text)

    if tool_id == "trust_vs_fear_clarifier":
        from tools.relationship.trust_vs_fear_clarifier import handle
        return handle(step, user_text)

    if tool_id == "over_giving_recovery":
        from tools.relationship.over_giving_recovery import handle
        return handle(step, user_text)

    if tool_id == "resentment_drain":
        from tools.relationship.resentment_drain import handle
        return handle(step, user_text)

    if tool_id == "communication_freeze_breaker":
        from tools.relationship.communication_freeze_breaker import handle
        return handle(step, user_text)

    if tool_id == "post_argument_regulation":
        from tools.relationship.post_argument_regulation import handle
        return handle(step, user_text)

    if tool_id == "emotional_dependency_soften":
        from tools.relationship.emotional_dependency_soften import handle
        return handle(step, user_text)

    if tool_id == "relationship_reality_check":
        from tools.relationship.relationship_reality_check import handle
        return handle(step, user_text)

    if tool_id == "boundaries_in_love_tool":
        from tools.relationship.boundaries_in_love_tool import handle
        return handle(step, user_text)

    if tool_id == "let_go_without_cutting_off":
        from tools.relationship.let_go_without_cutting_off import handle
        return handle(step, user_text)

    # ====================
    # FALLBACK
    # ====================
    return {
        "step": "exit",
        "text": "Let’s pause here. I’m here if you want to continue later.",
    }
