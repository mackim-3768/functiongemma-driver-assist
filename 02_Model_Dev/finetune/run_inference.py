import sys
import json
from llama_cpp import Llama

# 1. Model Configuration
model_path = "finetune/functiongemma-270m.gguf"

print(f"Loading model from {model_path}...")
llm = Llama(
    model_path=model_path,
    n_ctx=2048,      # Context window
    n_gpu_layers=-1, # Offload all layers to GPU (MPS)
    verbose=False
)

# 2. Define a sample prompt with context
# FunctionGemma expects a specific format.
# We will use a sample from the driver_assist_finetune.jsonl dataset structure.

context_json = {
    "lane_departure": {
        "departed": False,
        "confidence": 0.16
    },
    "driver_drowsiness": {
        "drowsy": True,
        "confidence": 0.99
    },
    "steering_grip": {
        "hands_on": True
    },
    "vehicle_speed_kph": 49,
    "forward_collision_risk": 0.06,
    "driving_duration_minutes": 51,
    "lka_status": {
        "enabled": False
    },
    "driving_environment": {
        "weather": "clear",
        "road_condition": "dry",
        "visibility": "good"
    },
    "recent_warning_history": {
        "last_warning_type": "drowsiness",
        "seconds_ago": 30.0
    },
    "sensor_health_status": {
        "camera_ok": True,
        "ai_model_confidence": 0.86
    }
}

user_query = "Driver unresponsive to repeated warnings."

prompt = f"""<start_of_turn>user
You are FunctionGemma, a function selection model for a driver assistance demo.

Input context is structured sensor state (do not invent fields):
{json.dumps(context_json, indent=2)}

User prompt:
{user_query}

Return ONLY a JSON array of tool calls. Each item must be:
{{"name": "<tool_name>", "arguments": {{ ... }}}}

Allowed tool names:
- trigger_steering_vibration
- trigger_navigation_notification
- trigger_drowsiness_alert_sound
- trigger_cluster_visual_warning
- trigger_hud_warning
- trigger_voice_prompt
- escalate_warning_level
- trigger_rest_recommendation
- log_safety_event
- request_safe_mode

If no action is needed, return:
[{{"name":"log_safety_event","arguments":{{"message":"no_action_selected"}}}}]
<end_of_turn>
<start_of_turn>model
"""

print("\n--- Prompt ---")
print(prompt)
print("--------------\n")

# 3. Inference
print("Generating response...")
output = llm(
    prompt,
    max_tokens=256,
    stop=["<end_of_turn>"],
    echo=False
)

response_text = output['choices'][0]['text'].strip()
print("\n--- Model Response ---")
print(response_text)
print("----------------------")

# 4. Parse JSON
try:
    actions = json.loads(response_text)
    print("\nParsed Actions:")
    print(json.dumps(actions, indent=2))
except json.JSONDecodeError:
    print("\nFailed to parse JSON response.")
