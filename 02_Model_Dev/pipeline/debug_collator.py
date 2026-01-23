from transformers import AutoTokenizer
from trl import DataCollatorForCompletionOnlyLM
from datasets import load_dataset
import torch

def debug_collator():
    model_name = "google/functiongemma-270m-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load a sample from the dataset
    dataset_path = "pipeline/history/01_seed/train_finetune.jsonl"
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    sample = dataset[0]
    print(f"Sample text snippet: {sample['text'][-200:]}")

    # Create collator
    response_template = "<start_of_turn>model\n"
    collator = DataCollatorForCompletionOnlyLM(response_template, tokenizer=tokenizer)

    # Tokenize
    inputs = tokenizer([sample['text']], return_tensors="pt", max_length=1024, truncation=True, padding=False)
    
    # Apply collator
    # Collator expects a list of dicts with 'input_ids', 'attention_mask'
    features = [{"input_ids": inputs["input_ids"][0], "attention_mask": inputs["attention_mask"][0]}]
    batch = collator(features)
    
    labels = batch["labels"][0]
    input_ids = batch["input_ids"][0]
    
    print("\n--- Tokenized ---")
    print(f"Input IDs length: {len(input_ids)}")
    print(f"Labels length: {len(labels)}")
    
    # Check if we have any non -100 labels
    non_ignored = labels[labels != -100]
    print(f"Number of trained tokens: {len(non_ignored)}")
    
    if len(non_ignored) == 0:
        print("CRITICAL: All labels are -100. The template was NOT found.")
        # Debug tokenization of template
        template_ids = tokenizer.encode(response_template, add_special_tokens=False)
        print(f"Template IDs: {template_ids}")
        # Debug input ids around where we expect the template
        # Find where the template might be
        print("Searching for template sequence manually...")
    else:
        print("Success! Labels are correctly assigned.")
        print(f"First 10 trained tokens: {tokenizer.decode(non_ignored[:10])}")

if __name__ == "__main__":
    debug_collator()
