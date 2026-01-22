import json
import random
import os
import sys
import argparse
from datetime import datetime
import mlflow

# Add chatbot-tester to path if needed (assuming it's a sibling directory)
# In a real environment, it should be installed via pip
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../chatbot-tester/src')))

# Try to import chatbot_tester structures if available, otherwise use dicts
try:
    from chatbot_tester.generator.schema import sample_schema
except ImportError:
    pass

# --- 1. Logic ported from dataset_gen_v2.py ---

def generate_random_context():
    # Expanded scenarios
    scenario_type = random.choices(
        [
            "normal", 
            "drowsy", 
            "lane_departure", 
            "hands_off", 
            "collision_risk", 
            "complex", 
            "sensor_fail",
            "bad_weather",
            "safe_mode_needed"
        ],
        weights=[0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    )[0]

    # Base Context
    context = {
        "lane_departure": {"departed": False, "confidence": round(random.uniform(0.0, 0.3), 2)},
        "driver_drowsiness": {"drowsy": False, "confidence": round(random.uniform(0.0, 0.3), 2)},
        "steering_grip": {"hands_on": True},
        "vehicle_speed_kph": random.randint(40, 110),
        "forward_collision_risk": round(random.uniform(0.0, 0.3), 2),
        "driving_duration_minutes": random.randint(10, 120),
        "lka_status": {"enabled": random.choice([True, True, False])},
        "driving_environment": {
            "weather": "clear",
            "road_condition": "dry",
            "visibility": "good"
        },
        "recent_warning_history": {
            "last_warning_type": "none",
            "seconds_ago": float(random.randint(300, 86400))
        },
        "sensor_health_status": {
            "camera_ok": True,
            "ai_model_confidence": round(random.uniform(0.8, 1.0), 2)
        }
    }

    prompt_hint = "Monitor status."

    # Modify context based on scenario
    if scenario_type == "drowsy":
        context["driver_drowsiness"] = {"drowsy": True, "confidence": round(random.uniform(0.8, 0.99), 2)}
        context["recent_warning_history"] = {"last_warning_type": "drowsiness", "seconds_ago": float(random.randint(60, 300))}
        prompt_hint = random.choice(["User looks tired.", "Drowsiness detected.", "Check driver status."])
    
    elif scenario_type == "lane_departure":
        context["lane_departure"] = {"departed": True, "confidence": round(random.uniform(0.7, 0.99), 2)}
        context["vehicle_speed_kph"] = random.randint(70, 130)
        context["lka_status"]["enabled"] = False 
        prompt_hint = random.choice(["Lane departure warning.", "Car is drifting.", "Stay in lane."])

    elif scenario_type == "hands_off":
        context["steering_grip"] = {"hands_on": False}
        prompt_hint = random.choice(["Hands off steering wheel.", "Driver hands not detected.", "Grab the wheel."])

    elif scenario_type == "collision_risk":
        context["forward_collision_risk"] = round(random.uniform(0.75, 0.99), 2)
        prompt_hint = random.choice(["Collision warning!", "Brake now!", "Obstacle ahead."])

    elif scenario_type == "complex":
        context["driver_drowsiness"] = {"drowsy": True, "confidence": round(random.uniform(0.85, 0.99), 2)}
        context["lane_departure"] = {"departed": True, "confidence": round(random.uniform(0.75, 0.99), 2)}
        context["vehicle_speed_kph"] = random.randint(90, 140)
        prompt_hint = "Emergency: Drowsy and drifting at high speed."

    elif scenario_type == "sensor_fail":
        context["sensor_health_status"] = {"camera_ok": False, "ai_model_confidence": 0.0}
        prompt_hint = "System error. Camera lost."

    elif scenario_type == "bad_weather":
        context["driving_environment"] = {
            "weather": random.choice(["rain", "snow", "fog"]),
            "road_condition": random.choice(["wet", "icy", "snowy"]),
            "visibility": "poor"
        }
        prompt_hint = "Weather condition changed."

    elif scenario_type == "safe_mode_needed":
        context["driver_drowsiness"] = {"drowsy": True, "confidence": 0.99}
        context["recent_warning_history"] = {"last_warning_type": "drowsiness", "seconds_ago": 30.0}
        prompt_hint = "Driver unresponsive to repeated warnings."

    return context, prompt_hint, scenario_type

def determine_actions(context, prompt):
    actions = []
    
    lane = context["lane_departure"]
    drowsy = context["driver_drowsiness"]
    hands = context["steering_grip"]
    speed = context["vehicle_speed_kph"]
    risk = context["forward_collision_risk"]
    env = context["driving_environment"]
    health = context["sensor_health_status"]
    history = context["recent_warning_history"]
    lka = context["lka_status"]
    
    # Priority 0: Sensor Health
    if not health["camera_ok"]:
        actions.append({"name": "trigger_cluster_visual_warning", "arguments": {"message": "Camera Fail. System Disabled.", "level": "critical"}})
        actions.append({"name": "log_safety_event", "arguments": {"message": "sensor_failure_camera"}})
        return actions

    # Priority 1: Safe Mode
    if drowsy["drowsy"] and history["last_warning_type"] == "drowsiness" and history["seconds_ago"] < 60:
        actions.append({"name": "request_safe_mode", "arguments": {"reason": "Driver unresponsive to drowsiness warnings"}})
        actions.append({"name": "trigger_voice_prompt", "arguments": {"message": "Pulling over safely.", "level": "critical"}})
        actions.append({"name": "escalate_warning_level", "arguments": {"level": "critical"}})
        return actions

    # Logic 2: Drowsiness
    if drowsy["drowsy"] and drowsy["confidence"] >= 0.8:
        actions.append({"name": "trigger_drowsiness_alert_sound", "arguments": {"volume_percent": 100}})
        actions.append({"name": "trigger_voice_prompt", "arguments": {"message": "Are you drowsy? Please take a rest.", "level": "critical"}})
        actions.append({"name": "trigger_rest_recommendation", "arguments": {"reason": "Drowsiness detected"}})
        actions.append({"name": "escalate_warning_level", "arguments": {"level": "critical"}})

    # Logic 3: Lane Departure
    if lane["departed"] and lane["confidence"] >= 0.7:
        intensity = "high" if speed >= 90 else "medium"
        actions.append({"name": "trigger_steering_vibration", "arguments": {"intensity": intensity}})
        actions.append({"name": "trigger_hud_warning", "arguments": {"message": "Lane Departure", "level": "warning"}})
        
        if not lka["enabled"]:
             actions.append({"name": "trigger_cluster_visual_warning", "arguments": {"message": "LKA is OFF", "level": "warning"}})

    # Logic 4: Hands Off
    if not hands["hands_on"]:
        actions.append({"name": "trigger_cluster_visual_warning", "arguments": {"message": "Keep hands on wheel", "level": "warning"}})
        if speed >= 100:
             actions.append({"name": "trigger_voice_prompt", "arguments": {"message": "Please hold the steering wheel.", "level": "warning"}})

    # Logic 5: Collision Risk
    if risk >= 0.75:
        actions.append({"name": "trigger_hud_warning", "arguments": {"message": "COLLISION WARNING", "level": "critical"}})
        actions.append({"name": "trigger_cluster_visual_warning", "arguments": {"message": "BRAKE!", "level": "critical"}})
        actions.append({"name": "escalate_warning_level", "arguments": {"level": "critical"}})

    # Logic 6: Environmental Warnings
    if env["weather"] in ["rain", "snow", "fog"] or env["road_condition"] in ["icy", "snowy"]:
        if risk < 0.75:
             actions.append({"name": "trigger_navigation_notification", "arguments": {"message": f"Bad weather: {env['weather']}. Drive carefully.", "level": "info"}})

    # Default
    if not actions:
        actions.append({"name": "log_safety_event", "arguments": {"message": "status_normal"}})

    # Deduplicate
    unique_actions = []
    seen = set()
    for a in actions:
        if a["name"] not in seen:
            unique_actions.append(a)
            seen.add(a["name"])
            
    return unique_actions

def construct_prompt(context, prompt_hint):
    return f"""You are FunctionGemma, a function selection model for a driver assistance demo.

Input context is structured sensor state (do not invent fields):
{json.dumps(context, indent=2)}

User prompt:
{prompt_hint}

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
"""

def format_for_finetuning(prompt_text, actions):
    # Function Gemma format
    input_text = f"<start_of_turn>user\n{prompt_text}<end_of_turn>\n<start_of_turn>model\n{json.dumps(actions)}<end_of_turn>"
    return {"text": input_text}

# --- 2. Generator Pipeline ---

def run_generator(output_dir, num_samples, seed):
    random.seed(seed)
    
    canonical_samples = []
    finetune_samples = []
    
    # Statistics
    tag_counts = {}
    
    print(f"Generating {num_samples} samples with seed {seed}...")
    
    for i in range(num_samples):
        ctx, prompt_hint, scenario_type = generate_random_context()
        actions = determine_actions(ctx, prompt_hint)
        
        # 1. Create Canonical Sample (Chatbot Tester Format)
        prompt_text = construct_prompt(ctx, prompt_hint)
        
        sample_id = f"gen_{seed}_{i:05d}"
        sample = {
            "id": sample_id,
            "messages": [
                {"role": "user", "content": prompt_text}
            ],
            "expected": actions, # The ground truth tool calls
            "tags": [scenario_type],
            "metadata": {
                "scenario": scenario_type,
                "complexity": len(actions)
            }
        }
        canonical_samples.append(sample)
        
        # Update stats
        tag_counts[scenario_type] = tag_counts.get(scenario_type, 0) + 1
        
        # 2. Create Finetune Sample (Function Gemma Format)
        finetune_entry = format_for_finetuning(prompt_text, actions)
        finetune_samples.append(finetune_entry)
        
    # Write files
    os.makedirs(output_dir, exist_ok=True)
    
    # Save Canonical Dataset
    canonical_path = os.path.join(output_dir, "dataset_canonical.jsonl")
    with open(canonical_path, "w") as f:
        for s in canonical_samples:
            f.write(json.dumps(s) + "\n")
            
    # Save Finetune Dataset
    finetune_path = os.path.join(output_dir, "dataset_finetune.jsonl")
    with open(finetune_path, "w") as f:
        for s in finetune_samples:
            f.write(json.dumps(s) + "\n")

    # Save Metadata
    metadata = {
        "dataset_id": "driver_assist_generated",
        "version": "v1.0",
        "created_at": datetime.now().isoformat(),
        "sample_count": num_samples,
        "seed": seed,
        "tag_stats": tag_counts
    }
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Saved artifacts to {output_dir}")
    return canonical_path, finetune_path, metadata_path, metadata

# --- 3. MLflow Entry Point ---

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="data_output")
    args = parser.parse_args()
    
    # Start MLflow run
    # Note: In a nested pipeline, this might be a child run.
    # We check if an active run exists.
    active_run = mlflow.active_run()
    
    if active_run:
        print(f"Attach to existing run: {active_run.info.run_id}")
    else:
        print("Starting new MLflow run...")
        mlflow.start_run(run_name="data_generation")

    try:
        # Log parameters
        mlflow.log_param("gen_samples", args.samples)
        mlflow.log_param("gen_seed", args.seed)
        
        # Execute generation
        c_path, f_path, m_path, meta = run_generator(args.output_dir, args.samples, args.seed)
        
        # Log artifacts
        mlflow.log_artifact(c_path)
        mlflow.log_artifact(f_path)
        mlflow.log_artifact(m_path)
        
        # Log metrics/tags
        mlflow.set_tag("dataset_version", meta["version"])
        for tag, count in meta["tag_stats"].items():
            mlflow.log_metric(f"count_{tag}", count)
            
    finally:
        if not active_run:
            mlflow.end_run()

if __name__ == "__main__":
    main()
