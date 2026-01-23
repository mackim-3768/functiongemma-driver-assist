import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def debug_inference():
    base_model_name = "google/functiongemma-270m-it"
    adapter_path = "pipeline/history/01_seed/run_v4/final_model"
    
    print(f"Loading base model: {base_model_name}")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    
    # Check tokenizer special tokens
    print(f"Tokenizer pad_token_id: {tokenizer.pad_token_id}")
    print(f"Tokenizer eos_token_id: {tokenizer.eos_token_id}")
    
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float32,
        device_map="auto",
        trust_remote_code=True
    )
    
    print(f"Loading adapter from: {adapter_path}")
    model = PeftModel.from_pretrained(base_model, adapter_path)
    
    # Check for NaNs in adapter
    print("Checking for NaNs in adapter parameters...")
    has_nan = False
    for name, param in model.named_parameters():
        if "lora" in name: # Check LoRA parameters
            if torch.isnan(param).any() or torch.isinf(param).any():
                print(f"NaN/Inf found in {name}")
                has_nan = True
    
    if has_nan:
        print("CRITICAL: Adapter contains NaN/Inf values. Training likely failed.")
    else:
        print("Adapter weights seem numerically valid (no NaNs).")
        
    model.eval()
    
    # Simple prompt
    prompt = """<start_of_turn>user
You are FunctionGemma.
User looks tired.
Return ONLY a JSON array of tool calls.
<end_of_turn>
<start_of_turn>model
"""
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    print(f"Input tokens: {inputs['input_ids']}")
    print(f"Attention mask: {inputs['attention_mask']}")
    
    print("Generating...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            do_sample=False,
            temperature=0.0,
            pad_token_id=tokenizer.eos_token_id # Explicitly set pad_token_id
        )
        
    print(f"Output tokens: {outputs[0]}")
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=False)
    print(f"Generated text:\n{generated_text}")

if __name__ == "__main__":
    debug_inference()
