import json
import random

# 1. Define Structures mimicking the Kotlin App

def generate_random_context():
    # Base probabilities for scenarios
    scenario_type = random.choices(
        ["normal", "drowsy", "lane_departure", "hands_off", "collision_risk", "complex"],
        weights=[0.3, 0.15, 0.15, 0.15, 0.15, 0.1]
    )[0]

    context = {
        "lane_departure": {"departed": False, "confidence": round(random.uniform(0.0, 0.3), 2)},
        "driver_drowsiness": {"drowsy": False, "confidence": round(random.uniform(0.0, 0.3), 2)},
        "steering_grip": {"hands_on": True},
        "vehicle_speed_kph": random.randint(40, 110),
        "forward_collision_risk": round(random.uniform(0.0, 0.3), 2),
        "driving_duration_minutes": random.randint(10, 120)
    }

    prompt_hint = "Monitor status."

    if scenario_type == "drowsy":
        context["driver_drowsiness"] = {"drowsy": True, "confidence": round(random.uniform(0.8, 0.99), 2)}
        prompt_hint = random.choice(["User looks tired.", "Drowsiness detected.", "Check driver status."])
    
    elif scenario_type == "lane_departure":
        context["lane_departure"] = {"departed": True, "confidence": round(random.uniform(0.7, 0.99), 2)}
        context["vehicle_speed_kph"] = random.randint(70, 130)
        prompt_hint = random.choice(["Lane departure warning.", "Car is drifting.", "Stay in lane."])

    elif scenario_type == "hands_off":
        context["steering_grip"] = {"hands_on": False}
        prompt_hint = random.choice(["Hands off steering wheel.", "Driver hands not detected.", "Grab the wheel."])

    elif scenario_type == "collision_risk":
        context["forward_collision_risk"] = round(random.uniform(0.75, 0.99), 2)
        prompt_hint = random.choice(["Collision warning!", "Brake now!", "Obstacle ahead."])

    elif scenario_type == "complex":
        # Drowsy + Lane Departure + High Speed
        context["driver_drowsiness"] = {"drowsy": True, "confidence": round(random.uniform(0.85, 0.99), 2)}
        context["lane_departure"] = {"departed": True, "confidence": round(random.uniform(0.75, 0.99), 2)}
        context["vehicle_speed_kph"] = random.randint(90, 140)
        prompt_hint = "Emergency: Drowsy and drifting at high speed."

    return context, prompt_hint, scenario_type

# 2. Rule-based Oracle (The "Teacher" Logic)
def determine_actions(context, prompt):
    actions = []
    
    lane = context["lane_departure"]
    drowsy = context["driver_drowsiness"]
    hands = context["steering_grip"]
    speed = context["vehicle_speed_kph"]
    risk = context["forward_collision_risk"]
    
    # Logic 1: Drowsiness
    if drowsy["drowsy"] and drowsy["confidence"] >= 0.8:
        actions.append({"name": "trigger_drowsiness_alert_sound", "arguments": {"volume_percent": 100}})
        actions.append({"name": "trigger_voice_prompt", "arguments": {"message": "Are you drowsy? Please take a rest.", "level": "critical"}})
        actions.append({"name": "trigger_rest_recommendation", "arguments": {}})
        actions.append({"name": "escalate_warning_level", "arguments": {"level": "critical"}})

    # Logic 2: Lane Departure
    if lane["departed"] and lane["confidence"] >= 0.7:
        intensity = "high" if speed >= 90 else "medium"
        actions.append({"name": "trigger_steering_vibration", "arguments": {"intensity": intensity}})
        actions.append({"name": "trigger_hud_warning", "arguments": {"message": "Lane Departure", "level": "warning"}})

    # Logic 3: Hands Off
    if not hands["hands_on"]:
        actions.append({"name": "trigger_cluster_visual_warning", "arguments": {"message": "Keep hands on wheel", "level": "warning"}})
        if speed >= 100:
             actions.append({"name": "trigger_voice_prompt", "arguments": {"message": "Please hold the steering wheel.", "level": "warning"}})

    # Logic 4: Collision Risk
    if risk >= 0.75:
        actions.append({"name": "trigger_hud_warning", "arguments": {"message": "COLLISION WARNING", "level": "critical"}})
        actions.append({"name": "trigger_cluster_visual_warning", "arguments": {"message": "BRAKE!", "level": "critical"}})
        actions.append({"name": "escalate_warning_level", "arguments": {"level": "critical"}})

    # Default: Log if nothing else
    if not actions:
        actions.append({"name": "log_safety_event", "arguments": {"message": "status_normal"}})

    # Deduplicate by name (simple version)
    unique_actions = []
    seen = set()
    for a in actions:
        if a["name"] not in seen:
            unique_actions.append(a)
            seen.add(a["name"])
            
    return unique_actions

# 3. Format for Function Gemma (Chat Template)
def format_to_gemma_jsonl(context, prompt, actions):
    # System prompt is implicit or part of the first user turn in some finetuning pipelines.
    # We will use the standard chat format: user -> model
    
    input_text = f"""<start_of_turn>user
You are FunctionGemma, a function selection model for a driver assistance demo.

Input context is structured sensor state (do not invent fields):
{json.dumps(context, indent=2)}

User prompt:
{prompt}

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
{json.dumps(actions)}<end_of_turn>"""
    
    return {"text": input_text}

# 4. Generate Dataset
def main():
    dataset = []
    for _ in range(1000): # Generate 1000 samples
        ctx, prompt, _ = generate_random_context()
        actions = determine_actions(ctx, prompt)
        entry = format_to_gemma_jsonl(ctx, prompt, actions)
        dataset.append(entry)
    
    with open("driver_assist_finetune.jsonl", "w") as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")
            
    print(f"Generated {len(dataset)} samples in driver_assist_finetune.jsonl")

if __name__ == "__main__":
    main()
