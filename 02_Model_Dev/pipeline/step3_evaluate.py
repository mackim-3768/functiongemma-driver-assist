import argparse
import json
import os
import mlflow
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import numpy as np
from tqdm import tqdm
from openai import OpenAI

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

def _extract_json_from_text(text: str):
    cleaned = (text or "").strip()
    if not cleaned:
        raise json.JSONDecodeError("empty", cleaned, 0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        if "```json" in cleaned:
            extracted = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
            return json.loads(extracted)
        if "```" in cleaned:
            extracted = cleaned.split("```", 1)[1].split("```", 1)[0].strip()
            return json.loads(extracted)
        raise

def geval_judge_tool_calls(
    client: OpenAI,
    judge_model: str,
    user_prompt: str,
    expected_tool_calls,
    predicted_text: str,
):
    prompt = (
        "You are an evaluator for tool-calling outputs. "
        "Given a user prompt, an expected list of tool calls, and a model prediction, "
        "decide whether the prediction is correct. "
        "A prediction is correct if it represents the same tool calls as expected, "
        "allowing harmless formatting differences (whitespace, key order). "
        "If the prediction is not valid JSON, it is incorrect. "
        "Return ONLY a JSON object with fields: verdict (boolean), reason (string).\n\n"
        f"USER_PROMPT:\n{user_prompt}\n\n"
        f"EXPECTED_TOOL_CALLS_JSON:\n{json.dumps(expected_tool_calls, ensure_ascii=False)}\n\n"
        f"PREDICTED_TEXT:\n{predicted_text}\n"
    )

    resp = client.responses.create(
        model=judge_model,
        input=prompt,
    )
    content = getattr(resp, "output_text", None) or ""
    obj = _extract_json_from_text(content)
    verdict = bool(obj.get("verdict"))
    reason = str(obj.get("reason", ""))
    return verdict, reason, content

def run_evaluation(
    model_path,
    dataset_path,
    base_model_name,
    output_dir,
    enable_geval=False,
    geval_model="gpt-4o-mini",
    geval_max_samples=0,
):
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

    enable_geval = bool(enable_geval)
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if enable_geval and not openai_api_key:
        enable_geval = False
        mlflow.set_tag("geval_status", "skipped_no_openai_api_key")

    openai_client = OpenAI(api_key=openai_api_key) if enable_geval else None
    geval_judged = 0
    geval_correct = 0
    geval_results = []
    
    print(f"Evaluating {len(samples)} samples...")
    
    # Import Metric
    # from chatbot_tester.evaluator.metrics.tool_call import ToolCallMatchMetric
    from utils.metric_utils import ToolCallMatchMetric
    
    for sample in tqdm(samples):
        # Extract user prompt from canonical format
        user_msg = next((m["content"] for m in sample["messages"] if m["role"] == "user"), "")
        
        predicted_str = run_inference(model, tokenizer, user_msg)
        expected_obj = sample["expected"]
        
        is_match, reason, pred_obj = ToolCallMatchMetric.match(predicted_str, expected_obj)

        geval_verdict = None
        geval_reason = None
        geval_raw = None
        if openai_client is not None:
            if (geval_max_samples or 0) <= 0 or geval_judged < int(geval_max_samples):
                try:
                    geval_verdict, geval_reason, geval_raw = geval_judge_tool_calls(
                        client=openai_client,
                        judge_model=geval_model,
                        user_prompt=user_msg,
                        expected_tool_calls=expected_obj,
                        predicted_text=predicted_str,
                    )
                    geval_judged += 1
                    if geval_verdict:
                        geval_correct += 1
                except Exception as e:
                    geval_verdict = False
                    geval_reason = f"geval_exception_{type(e).__name__}"
                    geval_raw = str(e)
                    geval_judged += 1

                geval_results.append(
                    {
                        "id": sample["id"],
                        "verdict": bool(geval_verdict),
                        "reason": geval_reason,
                        "judge_model": geval_model,
                        "raw": geval_raw,
                    }
                )
        
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
            "tags": sample.get("tags", []),
            "geval_verdict": geval_verdict,
            "geval_reason": geval_reason,
        })
        
    # Metrics
    accuracy = correct_count / len(samples) if samples else 0
    json_validity = valid_json_count / len(samples) if samples else 0
    
    metrics = {
        "accuracy_total": accuracy,
        "json_validity_score": json_validity
    }

    if openai_client is not None and geval_judged > 0:
        metrics["accuracy_geval"] = geval_correct / float(geval_judged)
        metrics["geval_judged_count"] = float(geval_judged)
        mlflow.set_tag("geval_status", "enabled")
        mlflow.set_tag("geval_model", geval_model)
    
    # Add per-tag accuracy
    for tag, stat in tag_stats.items():
        tag_acc = stat["correct"] / stat["total"] if stat["total"] > 0 else 0
        metrics[f"accuracy_{tag}"] = tag_acc
        
    # Save detailed results
    os.makedirs(output_dir, exist_ok=True)
    results_path = os.path.join(output_dir, "eval_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    geval_path = None
    if openai_client is not None and len(geval_results) > 0:
        geval_path = os.path.join(output_dir, "geval_results.json")
        with open(geval_path, "w") as f:
            json.dump(geval_results, f, indent=2)
        
    print(f"Evaluation Complete. Accuracy: {accuracy:.2%}, Valid JSON: {json_validity:.2%}")
    return metrics, results_path, geval_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, required=True, help="Path to adapter (step 2 output)")
    parser.add_argument("--dataset-path", type=str, required=True, help="Path to dataset_canonical.jsonl (step 1 output)")
    parser.add_argument("--base-model", type=str, default="google/functiongemma-270m-it")
    parser.add_argument("--output-dir", type=str, default="eval_output")
    parser.add_argument("--experiment-name", type=str, default=None, help="MLflow experiment name for standalone run")
    parser.add_argument("--geval", action="store_true", help="Enable OpenAI G-Eval judging")
    parser.add_argument("--geval-model", type=str, default="gpt-4o-mini")
    parser.add_argument("--geval-max-samples", type=int, default=0, help="0 means judge all samples")
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
        metrics, results_path, geval_path = run_evaluation(
            args.model_path, 
            args.dataset_path, 
            args.base_model,
            args.output_dir,
            enable_geval=args.geval,
            geval_model=args.geval_model,
            geval_max_samples=args.geval_max_samples,
        )
        
        # Log metrics
        for k, v in metrics.items():
            mlflow.log_metric(k, v)
            
        # Log artifact
        mlflow.log_artifact(results_path)

        if geval_path:
            mlflow.log_artifact(geval_path)
        
    finally:
        if not active_run:
            mlflow.end_run()

if __name__ == "__main__":
    main()
