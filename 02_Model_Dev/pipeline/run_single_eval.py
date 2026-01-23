import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

def load_model(base_model_name, adapter_path):
    print(f"Loading tokenizer from: {adapter_path}")
    tokenizer = AutoTokenizer.from_pretrained(adapter_path, trust_remote_code=True)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token

    force_device = os.environ.get("FORCE_DEVICE")
    device = force_device or ("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    dtype = torch.float16 if device == "cuda" else torch.float32

    print(f"Loading base model: {base_model_name}")
    print(f"Using device: {device}, dtype: {dtype}")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=dtype,
        trust_remote_code=True
    ).to(device)
    
    print(f"Loading adapter from: {adapter_path}")
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model = model.to(dtype=dtype)
    model.eval()
    
    return model, tokenizer

def run_inference(model, tokenizer, prompt):
    # FunctionGemma prompt format for inference
    cleaned_prompt = prompt.strip()
    if cleaned_prompt.endswith("<end_of_turn>"):
        cleaned_prompt = cleaned_prompt[: -len("<end_of_turn>")].rstrip()

    formatted_prompt = (
        f"<start_of_turn>user\n{cleaned_prompt}\n<end_of_turn>\n"
        f"<start_of_turn>model\n"
    )

    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    pad_token_id = tokenizer.pad_token_id
    eos_token_id = tokenizer.eos_token_id

    if model.config.pad_token_id is None and pad_token_id is not None:
        model.config.pad_token_id = pad_token_id
    if model.config.eos_token_id is None and eos_token_id is not None:
        model.config.eos_token_id = eos_token_id

    print(f"tokenizer.pad_token={tokenizer.pad_token!r} pad_token_id={tokenizer.pad_token_id}")
    print(f"tokenizer.eos_token={tokenizer.eos_token!r} eos_token_id={tokenizer.eos_token_id}")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False, # Deterministic for eval
            temperature=0.0,
            pad_token_id=pad_token_id,
            eos_token_id=eos_token_id,
            bad_words_ids=[[pad_token_id]] if pad_token_id is not None else None
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=False)
    
    # Extract model response part
    try:
        parts = generated_text.split("<start_of_turn>model\n")
        if len(parts) > 1:
            response_part = parts[1].split("<end_of_turn>")[0]
            return response_part.strip(), generated_text
    except:
        pass
        
    return generated_text, generated_text

def main():
    # Configuration
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    
    base_model_name = "google/functiongemma-270m-it"
    adapter_path = os.path.join(base_dir, "history/01_seed/run_v4/final_model")
    dataset_path = os.path.join(base_dir, "history/01_seed/eval_canonical.jsonl")
    target_id = "seed_00686"
    
    # Load Dataset and find sample
    print(f"Loading dataset: {dataset_path}")
    target_sample = None
    with open(dataset_path, "r") as f:
        for line in f:
            sample = json.loads(line)
            if sample["id"] == target_id:
                target_sample = sample
                break
    
    if not target_sample:
        print(f"Sample {target_id} not found!")
        return

    print(f"Found sample: {target_id}")
    
    # Extract user prompt
    user_msg = next((m["content"] for m in target_sample["messages"] if m["role"] == "user"), "")
    expected_obj = target_sample["expected"]
    
    print("-" * 50)
    print("INPUT PROMPT:")
    print(user_msg)
    print("-" * 50)
    print("EXPECTED OUTPUT:")
    print(json.dumps(expected_obj, indent=2))
    print("-" * 50)

    # Load Model
    model, tokenizer = load_model(base_model_name, adapter_path)
    
    # Run Inference
    print("Running inference...")
    predicted_str, full_text = run_inference(model, tokenizer, user_msg)
    
    print("-" * 50)
    print("MODEL OUTPUT:")
    print(predicted_str)
    print("-" * 50)
    
    # Basic validation
    try:
        predicted_json = json.loads(predicted_str)
        print("Valid JSON: Yes")
        
        # Compare roughly
        print("Parsed Result:")
        print(json.dumps(predicted_json, indent=2))
    except json.JSONDecodeError as e:
        print(f"Valid JSON: No ({e})")

if __name__ == "__main__":
    main()
