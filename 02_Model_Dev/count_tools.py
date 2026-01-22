import json
import collections

context_tools = [
    "get_lane_departure_status",
    "get_driver_drowsiness_status",
    "get_steering_grip_status",
    "get_vehicle_speed",
    "get_lka_status",
    "get_forward_collision_risk",
    "get_driving_environment",
    "get_driving_duration_status",
    "get_recent_warning_history",
    "get_sensor_health_status"
]

action_tools = [
    "trigger_steering_vibration",
    "trigger_navigation_notification",
    "trigger_drowsiness_alert_sound",
    "trigger_cluster_visual_warning",
    "trigger_hud_warning",
    "trigger_voice_prompt",
    "escalate_warning_level",
    "trigger_rest_recommendation",
    "log_safety_event",
    "request_safe_mode"
]

counts = collections.defaultdict(int)
total_lines = 0

with open('driver_assist_finetune.jsonl', 'r') as f:
    for line in f:
        total_lines += 1
        # We can just search in the line string for simplicity and speed
        # This might slightly overcount if names appear in non-call contexts, but for a quick check it's fine.
        # Ideally we parse JSON, but if the file is huge or complex, simple string search is faster for a first pass.
        # Given the request is about "usage", let's parse to be accurate about tool calls vs definitions.
        try:
            data = json.loads(line)
            # Check for tool calls in 'messages' or equivalent structure
            # Usually finetune data for function calling has a specific structure.
            # Let's look for tool names recursively in the JSON object.
            
            str_dump = json.dumps(data)
            for tool in context_tools + action_tools:
                if f'"{tool}"' in str_dump:
                     counts[tool] += 1
        except json.JSONDecodeError:
            pass

print(f"Total lines: {total_lines}")
print("\nContext Tools:")
for tool in context_tools:
    print(f"{tool}: {counts[tool]}")

print("\nAction Tools:")
for tool in action_tools:
    print(f"{tool}: {counts[tool]}")
