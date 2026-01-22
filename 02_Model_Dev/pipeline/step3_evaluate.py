import argparse
import json
import os
import mlflow
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import numpy as np
from tqdm import tqdm

def load_model(base_model_name, adapter_path):
    print(f"Loading base model: {base_model_name}")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    
    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Load adapter
    print(f"Loading adapter from: {adapter_path}")
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model.eval()
    
    return model, tokenizer

def run_inference(model, tokenizer, prompt):
    # FunctionGemma prompt format for inference
    formatted_prompt = f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
    
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False, # Deterministic for eval
            temperature=0.0
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=False)
    
    # Extract model response part
    # Look for <start_of_turn>model\n and take everything after until <end_of_turn>
    try:
        parts = generated_text.split("<start_of_turn>model\n")
        if len(parts) > 1:
            response_part = parts[1].split("<end_of_turn>")[0]
            return response_part.strip()
    except:
        pass
        
    return generated_text # Fallback


def run_evaluation(model_path, dataset_path, base_model_name, output_dir):
    # Load Model
    model, tokenizer = load_model(base_model_name, model_path)
    
    # Load Dataset
    print(f"Loading validation dataset: {dataset_path}")
    with open(dataset_path, "r") as f:
        lines = f.readlines()
        
    samples = [json.loads(line) for line in lines]
    
    results = []
    correct_count = 0
    valid_json_count = 0
    
    # Tag breakdown
    tag_stats = {}
    
    print(f"Evaluating {len(samples)} samples...")
    
    # Import Metric
    from chatbot_tester.evaluator.metrics.tool_call import ToolCallMatchMetric
    
    for sample in tqdm(samples):
        # Extract user prompt from canonical format
        user_msg = next((m["content"] for m in sample["messages"] if m["role"] == "user"), "")
        
        predicted_str = run_inference(model, tokenizer, user_msg)
        expected_obj = sample["expected"]
        
        is_match, reason, pred_obj = ToolCallMatchMetric.match(predicted_str, expected_obj)
        
        if pred_obj is not None:
            valid_json_count += 1
            
        if is_match:
            correct_count += 1
            
        # Update tag stats
        for tag in sample.get("tags", []):
            if tag not in tag_stats:
                tag_stats[tag] = {"total": 0, "correct": 0}
            tag_stats[tag]["total"] += 1
            if is_match:
                tag_stats[tag]["correct"] += 1
                
        results.append({
            "id": sample["id"],
            "input": user_msg,
            "expected": expected_obj,
            "predicted_raw": predicted_str,
            "predicted_parsed": pred_obj,
            "is_correct": is_match,
            "error_type": reason, 
            "tags": sample.get("tags", [])
        })
        
    # Metrics
    accuracy = correct_count / len(samples) if samples else 0
    json_validity = valid_json_count / len(samples) if samples else 0
    
    metrics = {
        "accuracy_total": accuracy,
        "json_validity_score": json_validity
    }
    
    # Add per-tag accuracy
    for tag, stat in tag_stats.items():
        tag_acc = stat["correct"] / stat["total"] if stat["total"] > 0 else 0
        metrics[f"accuracy_{tag}"] = tag_acc
        
    # Save detailed results
    os.makedirs(output_dir, exist_ok=True)
    results_path = os.path.join(output_dir, "eval_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Evaluation Complete. Accuracy: {accuracy:.2%}, Valid JSON: {json_validity:.2%}")
    return metrics, results_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, required=True, help="Path to adapter (step 2 output)")
    parser.add_argument("--dataset-path", type=str, required=True, help="Path to dataset_canonical.jsonl (step 1 output)")
    parser.add_argument("--base-model", type=str, default="google/functiongemma-270m-it")
    parser.add_argument("--output-dir", type=str, default="eval_output")
    parser.add_argument("--experiment-name", type=str, default=None, help="MLflow experiment name for standalone run")
    args = parser.parse_args()
    
    if args.experiment_name:
        mlflow.set_experiment(args.experiment_name)
    
    active_run = mlflow.active_run()
    if active_run:
        print(f"Attach to existing run: {active_run.info.run_id}")
    else:
        print("Starting new MLflow run...")
        mlflow.start_run(run_name="evaluation")
        
    try:
        metrics, results_path = run_evaluation(
            args.model_path, 
            args.dataset_path, 
            args.base_model,
            args.output_dir
        )
        
        # Log metrics
        for k, v in metrics.items():
            mlflow.log_metric(k, v)
            
        # Log artifact
        mlflow.log_artifact(results_path)
        
    finally:
        if not active_run:
            mlflow.end_run()

if __name__ == "__main__":
    main()
