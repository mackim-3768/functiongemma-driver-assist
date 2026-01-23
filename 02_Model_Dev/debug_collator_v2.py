import torch
from transformers import AutoTokenizer
from pipeline.utils.finetune_utils import CompletionOnlyDataCollator

def debug_collator():
    model_name = "google/functiongemma-270m-it"
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    response_template = "<start_of_turn>model\n"
    response_ids = tokenizer.encode(response_template, add_special_tokens=False)
    print(f"Response template: '{response_template}'")
    print(f"Response IDs: {response_ids}")
    
    collator = CompletionOnlyDataCollator(response_template, tokenizer, mlm=False)
    
    # Sample text from dataset
    sample_text = """<start_of_turn>user
You are FunctionGemma.
User looks tired.
Return ONLY a JSON array of tool calls.
<end_of_turn>
<start_of_turn>model
[{"name": "trigger_rest_recommendation", "arguments": {"reason": "User looks tired"}}]<end_of_turn>"""

    print("\n--- Sample Text ---")
    print(sample_text)
    
    # Tokenize
    inputs = tokenizer(sample_text, return_tensors=None) # get lists
    input_ids = inputs["input_ids"]
    print(f"\nTotal input length: {len(input_ids)}")
    
    # Create a batch
    batch_input = [{"input_ids": input_ids, "attention_mask": inputs["attention_mask"]}]
    
    # Run collator
    batch_output = collator.torch_call(batch_input)
    
    labels = batch_output["labels"][0]
    input_ids_tensor = batch_output["input_ids"][0]
    
    print("\n--- Labels Analysis ---")
    print(f"Labels length: {len(labels)}")
    
    # Check what is masked (-100) and what is not
    unmasked_indices = (labels != -100).nonzero(as_tuple=True)[0]
    
    if len(unmasked_indices) == 0:
        print("CRITICAL: All labels are masked (-100). The model will learn NOTHING.")
        
        # Debugging why
        print("Searching for response_ids in input_ids...")
        found = False
        len_template = len(response_ids)
        for j in range(len(input_ids) - len_template + 1):
            chunk = input_ids[j:j+len_template]
            if chunk == response_ids:
                print(f"Found template at index {j}")
                found = True
                break
            # print(f"Index {j}: {chunk} != {response_ids}")
            
        if not found:
            print("Template NOT found in input_ids.")
            print(f"First 20 input_ids: {input_ids[:20]}")
            print(f"Response IDs: {response_ids}")
            
    else:
        print(f"Unmasked {len(unmasked_indices)} tokens.")
        print("Unmasked tokens (what the model learns to predict):")
        for idx in unmasked_indices:
            token_id = input_ids_tensor[idx].item()
            token_label = labels[idx].item()
            token_str = tokenizer.decode([token_id])
            print(f"Idx {idx}: {token_id} ({token_str}) -> Label: {token_label}")
            
if __name__ == "__main__":
    debug_collator()
