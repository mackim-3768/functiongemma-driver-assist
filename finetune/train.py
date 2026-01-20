from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
import os

# 1. Configuration
max_seq_length = 2048 # Choose any! We auto support RoPE Scaling internally!
dtype = None # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
load_in_4bit = True # Use 4bit quantization to reduce memory usage. Can be False.

model_name = "google/gemma-1.1-2b-it" # Or "unsloth/gemma-1.1-2b-it-bnb-4bit"
new_model_name = "functiongemma-driver-assist-lora"
output_dir = "outputs"
dataset_file = "driver_assist_finetune.jsonl"

# 2. Load Model & Tokenizer
print(f"Loading model: {model_name}")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 3. Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0, # Supports any, but = 0 is optimized
    bias = "none",    # Supports any, but = "none" is optimized
    use_gradient_checkpointing = "unsloth", # True or "unsloth" for very long context
    random_state = 3407,
    use_rslora = False,  # We support rank stabilized LoRA
    loftq_config = None, # And LoftQ
)

# 4. Load Dataset
print(f"Loading dataset: {dataset_file}")
dataset = load_dataset("json", data_files=dataset_file, split="train")

# 5. Training Arguments
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False, # Can make training 5x faster for short sequences.
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # Increase this for real training (e.g., 300-500)
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = output_dir,
    ),
)

# 6. Train
print("Starting training...")
trainer_stats = trainer.train()
print("Training finished.")

# 7. Save GGUF
print("Saving GGUF...")
# Save to 8bit Q8_0
model.save_pretrained_gguf(new_model_name, tokenizer, quantization_method = "q8_0")
# model.save_pretrained_gguf(new_model_name, tokenizer, quantization_method = "f16")

print(f"Model saved to {new_model_name}")
print("You can now push this GGUF to your device.")
