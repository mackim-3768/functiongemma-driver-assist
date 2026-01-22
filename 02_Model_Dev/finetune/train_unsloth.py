import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
import os

# 1. Configuration
model_id = "google/functiongemma-270m-it"
output_dir = "outputs_270m"
dataset_file = "driver_assist_finetune.jsonl"
new_model_name = "functiongemma-270m-driver-assist"

# Check device
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# 2. Load Tokenizer & Model
tokenizer = AutoTokenizer.from_pretrained(model_id)
# 270m is small, so we can load it normally. 
# MPS supports bfloat16 on newer chips, otherwise float16 or float32.
torch_dtype = torch.bfloat16 if device != "cpu" else torch.float32

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map=device,
    torch_dtype=torch_dtype,
)

# 3. LoRA Configuration
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
)

model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

# 4. Load Dataset
print(f"Loading dataset: {dataset_file}")
# Assuming the script is run from the finetune directory, but the dataset is in the parent.
# Let's verify dataset path.
dataset_path = os.path.join(os.path.dirname(__file__), "..", dataset_file)
if not os.path.exists(dataset_path):
    dataset_path = dataset_file # Try local if above fails
    if not os.path.exists(dataset_path):
        # Try absolute path based on known structure
        dataset_path = "/Users/admin/01_Workspace/01_platform_hangang/01_function_gemma/02_functiongemma-driver-assist/driver_assist_finetune.jsonl"

print(f"Dataset path: {dataset_path}")
dataset = load_dataset("json", data_files=dataset_path, split="train")

# 5. Split Dataset (Train/Eval)
# Split 90% train, 10% test
dataset = dataset.train_test_split(test_size=0.1)
print(f"Dataset split: {len(dataset['train'])} train, {len(dataset['test'])} test")

# 6. Preprocessing
def preprocess_function(examples):
    # Ensure EOS token is appended
    inputs = [f"{text}{tokenizer.eos_token}" for text in examples["text"]]
    model_inputs = tokenizer(inputs, max_length=1024, truncation=True, padding="max_length")
    model_inputs["labels"] = model_inputs["input_ids"].copy()
    return model_inputs

tokenized_train_dataset = dataset["train"].map(preprocess_function, batched=True)
tokenized_eval_dataset = dataset["test"].map(preprocess_function, batched=True)

# 7. Training Arguments
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    max_steps=300,
    
    # Evaluation Strategy
    eval_strategy="steps",
    eval_steps=50,
    save_strategy="steps",
    save_steps=50,
    load_best_model_at_end=True, # Save the best model based on validation loss
    
    warmup_steps=30,
    optim="adamw_torch",
    fp16=False,
    bf16=True if device != "cpu" else False, # Enable bf16 for MPS/CUDA
    group_by_length=True,
    report_to="none"
)

# 8. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_eval_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# 8. Train
print("Starting training...")
trainer.train()
print("Training finished.")

# 9. Save Adapter
print(f"Saving adapter to {output_dir}/final_adapter")
trainer.save_model(os.path.join(output_dir, "final_adapter"))

# 10. Merge and Save
print("Merging model...")
# Reload base model in CPU to avoid memory issues during merge
base_model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cpu",
    torch_dtype=torch.float32 # Use float32 for safe merging on CPU
)
model_to_merge = PeftModel.from_pretrained(base_model, os.path.join(output_dir, "final_adapter"))
merged_model = model_to_merge.merge_and_unload()

save_path = f"merged_{new_model_name}"
print(f"Saving merged model to {save_path}")
merged_model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)

print("Done! You can now convert the merged model to GGUF using llama.cpp")
