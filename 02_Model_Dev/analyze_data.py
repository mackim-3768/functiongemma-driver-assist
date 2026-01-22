import json
import re
from collections import defaultdict

# Define the expected mappings based on observation and tool definitions
context_tool_map = {
    "get_lane_departure_status": "lane_departure",
    "get_driver_drowsiness_status": "driver_drowsiness",
    "get_steering_grip_status": "steering_grip",
    "get_vehicle_speed": "vehicle_speed_kph",
    "get_lka_status": "lka_status", # Guessing key name
    "get_forward_collision_risk": "forward_collision_risk",
    "get_driving_environment": "driving_environment", # Guessing
    "get_driving_duration_status": "driving_duration_minutes",
    "get_recent_warning_history": "recent_warning_history", # Guessing
    "get_sensor_health_status": "sensor_health_status" # Guessing
}

# Reverse map for counting
key_to_context_tool = {v: k for k, v in context_tool_map.items()}

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

context_counts = defaultdict(int)
action_counts = defaultdict(int)
total_samples = 0
malformed_samples = 0

with open('driver_assist_finetune.jsonl', 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            text = data.get('text', '')
            
            # Extract Input Context
            # Pattern: Input context is structured sensor state (do not invent fields):\n{...}\n\nUser prompt:
            context_match = re.search(r'Input context is structured sensor state \(do not invent fields\):\n(\{.*?\})\n\nUser prompt:', text, re.DOTALL)
            if context_match:
                try:
                    context_json_str = context_match.group(1)
                    context_data = json.loads(context_json_str)
                    
                    for key in context_data.keys():
                        # Count the key itself
                        # Also try to map it to a tool
                        # We track all keys found to see if there are any we missed
                        context_counts[key] += 1
                        
                except json.JSONDecodeError:
                    print("Failed to decode context JSON")
                    pass
            
            # Extract Model Response (Action Tools)
            # Pattern: <start_of_turn>model\n[...]
            model_match = re.search(r'<start_of_turn>model\n(\[.*?\])<end_of_turn>', text, re.DOTALL)
            if model_match:
                try:
                    actions_json_str = model_match.group(1)
                    actions_data = json.loads(actions_json_str)
                    
                    for action in actions_data:
                        name = action.get('name')
                        if name:
                            action_counts[name] += 1
                except json.JSONDecodeError:
                    print("Failed to decode action JSON")
                    pass
            
            total_samples += 1
            
        except json.JSONDecodeError:
            malformed_samples += 1

print(f"Total Samples: {total_samples}")
print(f"Malformed Lines: {malformed_samples}")

print("\n--- Context Keys Found in Input ---")
# Check against expected context tools
found_context_keys = set(context_counts.keys())
for tool, key in context_tool_map.items():
    count = context_counts.get(key, 0)
    print(f"Tool '{tool}' (Key '{key}'): {count}")

print("\n--- Other Context Keys Found ---")
for key, count in context_counts.items():
    if key not in context_tool_map.values():
        print(f"Key '{key}': {count}")

print("\n--- Action Tools Called ---")
for tool in action_tools:
    count = action_counts.get(tool, 0)
    print(f"Tool '{tool}': {count}")

print("\n--- Other Actions Called ---")
for tool, count in action_counts.items():
    if tool not in action_tools:
        print(f"Tool '{tool}': {count}")
