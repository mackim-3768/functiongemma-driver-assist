import json
import os
import random
import argparse
from collections import Counter

def analyze_and_split(canonical_path, finetune_path, output_dir, train_ratio=0.9, seed=42):
    random.seed(seed)
    
    print(f"Loading canonical dataset: {canonical_path}")
    with open(canonical_path, 'r') as f:
        canonical_data = [json.loads(line) for line in f]
        
    print(f"Loading finetune dataset: {finetune_path}")
    with open(finetune_path, 'r') as f:
        finetune_data = [json.loads(line) for line in f]
        
    if len(canonical_data) != len(finetune_data):
        print(f"Warning: Line counts mismatch! Canonical: {len(canonical_data)}, Finetune: {len(finetune_data)}")
        # Proceed with safe length
        min_len = min(len(canonical_data), len(finetune_data))
        canonical_data = canonical_data[:min_len]
        finetune_data = finetune_data[:min_len]
    
    # Analyze Scenarios and Update Tags
    scenario_counter = Counter()
    
    for item in canonical_data:
        current_tags = item.get("tags", [])
        
        # If tag is generic 'from_seed', try to infer actual scenario from content
        if "from_seed" in current_tags or not current_tags:
            try:
                # Extract context from user message
                user_msg = item["messages"][0]["content"]
                
                # Robust extraction based on known prompt structure
                marker_start = "Input context is structured sensor state (do not invent fields):\n"
                marker_end = "\n\nUser prompt:"
                
                s_idx = user_msg.find(marker_start)
                e_idx = user_msg.find(marker_end)
                
                if s_idx != -1 and e_idx != -1:
                    json_str = user_msg[s_idx + len(marker_start) : e_idx].strip()
                    ctx = json.loads(json_str)
                    
                    inferred_tag = "normal"
                    
                    # Heuristics (Priority order matching step1 generator)
                    if ctx.get("sensor_health_status", {}).get("camera_ok") is False:
                        inferred_tag = "sensor_fail"
                    elif ctx.get("driver_drowsiness", {}).get("drowsy") and ctx.get("recent_warning_history", {}).get("last_warning_type") == "drowsiness":
                        inferred_tag = "safe_mode_needed" # Approximation
                    elif ctx.get("driver_drowsiness", {}).get("drowsy"):
                        # Check for complex (drowsy + lane)
                        if ctx.get("lane_departure", {}).get("departed"):
                            inferred_tag = "complex"
                        else:
                            inferred_tag = "drowsy"
                    elif ctx.get("lane_departure", {}).get("departed"):
                        inferred_tag = "lane_departure"
                    elif ctx.get("steering_grip", {}).get("hands_on") is False:
                        inferred_tag = "hands_off"
                    elif ctx.get("forward_collision_risk", 0) >= 0.7:
                        inferred_tag = "collision_risk"
                    elif ctx.get("driving_environment", {}).get("weather") in ["rain", "snow", "fog"]:
                         inferred_tag = "bad_weather"
                    
                    # Update item tag
                    item["tags"] = [inferred_tag]
                    current_tags = [inferred_tag]
            except Exception as e:
                pass # Keep original tag if parsing fails
        
        if current_tags:
            scenario_counter.update(current_tags)
        else:
            scenario_counter["unknown"] += 1
            
    total_count = len(canonical_data)
    
    # Split Data
    indices = list(range(total_count))
    random.shuffle(indices)
    
    split_idx = int(total_count * train_ratio)
    train_indices = indices[:split_idx]
    eval_indices = indices[split_idx:]
    
    # Create Output Directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save Split Files
    splits = {
        "train": train_indices,
        "eval": eval_indices
    }
    
    for split_name, idx_list in splits.items():
        # Save Finetune Split (For Step 2 Training)
        ft_out = os.path.join(output_dir, f"{split_name}_finetune.jsonl")
        with open(ft_out, 'w') as f:
            for idx in idx_list:
                f.write(json.dumps(finetune_data[idx]) + "\n")
                
        # Save Canonical Split (For Step 3 Evaluation)
        cn_out = os.path.join(output_dir, f"{split_name}_canonical.jsonl")
        with open(cn_out, 'w') as f:
            for idx in idx_list:
                f.write(json.dumps(canonical_data[idx]) + "\n")
                
    print(f"Split complete: Train ({len(train_indices)}), Eval ({len(eval_indices)}) saved to {output_dir}")

    # Generate README.md
    readme_content = f"""# 🚗 Driver Assist Seed Dataset (v1.0)

## 📌 Overview
이 데이터셋은 **Function Gemma** 모델이 운전자 보조 시스템(Driver Assist) 도메인의 함수 호출(Function Calling)을 학습할 수 있는지 **가능성을 검증(Feasibility Test)** 하기 위해 생성된 초기 Seed 데이터셋입니다.

## 📊 Data Statistics
*   **Total Samples**: {total_count}
*   **Train Set**: {len(train_indices)} ({(len(train_indices)/total_count)*100:.1f}%)
*   **Eval Set**: {len(eval_indices)} ({(len(eval_indices)/total_count)*100:.1f}%)

### 🏷️ Scenario Distribution
다양한 운전 상황 시나리오가 포함되어 있으며, 분포는 다음과 같습니다.

| Scenario Tag | Count | Percentage |
| :--- | :--- | :--- |
"""
    
    # Sort by count desc
    for tag, count in scenario_counter.most_common():
        percentage = (count / total_count) * 100
        readme_content += f"| `{tag}` | {count} | {percentage:.1f}% |\n"

    readme_content += f"""
## 🎯 Purpose
1.  **Baseline Performance Check**: 기본적인 9가지 시나리오(졸음, 차선이탈 등)에 대해 모델이 올바른 JSON 포맷으로 도구를 호출하는지 확인.
2.  **Metric Setup**: Accuracy, JSON Validity 등 평가 지표 파이프라인이 정상 동작하는지 테스트.
3.  **Overfitting Test**: 소규모 데이터셋으로 파인튜닝 시 모델이 의도한 대로 행동을 교정하는지 확인.

## 📂 File Structure
*   `train_finetune.jsonl`: 학습용 데이터 (Function Gemma Format)
*   `eval_canonical.jsonl`: 평가용 데이터 (Ground Truth 포함, Chatbot Tester Format)
*   `eval_finetune.jsonl`: 학습 중 Loss 계산용 (Optional)

## 🚀 Usage
이 데이터셋은 `02_Model_Dev/pipeline` 의 `step2_finetune.py` 와 `step3_evaluate.py` 에서 즉시 사용할 수 있습니다.
"""

    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
        
    print(f"README.md generated at {readme_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", required=True, help="Path to canonical jsonl")
    parser.add_argument("--finetune", required=True, help="Path to finetune jsonl")
    parser.add_argument("--output-dir", required=True, help="Directory to save splits and readme")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    
    analyze_and_split(args.canonical, args.finetune, args.output_dir, seed=args.seed)
