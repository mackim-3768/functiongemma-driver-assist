import argparse
import os
import json
import mlflow
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

def run_finetuning(dataset_path, output_dir, model_name, epochs, batch_size, learning_rate):
    print(f"Loading dataset from {dataset_path}...")
    # Load dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    
    # Configure quantization (optional, for efficiency)
    # Note: 4-bit quantization (bitsandbytes) typically requires CUDA.
    # For Mac (MPS) or CPU, or small models like 270m, we can skip it.
    use_quantization = torch.cuda.is_available() and "270m" not in model_name
    
    bnb_config = None
    if use_quantization:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )

    print(f"Loading model {model_name} (Quantization: {use_quantization})...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.padding_side = 'right' # FunctionGemma/Gemma specific

    # LoRA Config
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"] # Common targets for Gemma
    )
    
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Training Args
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="no", # We do eval separately in step 3
        fp16=True,
        report_to=["mlflow"],
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        dataset_text_field="text", # The field generated in step 1
        max_seq_length=1024,
        tokenizer=tokenizer,
        args=training_args,
    )

    print("Starting training...")
    trainer.train()
    
    # Save Model
    final_model_path = os.path.join(output_dir, "final_model")
    trainer.save_model(final_model_path)
    print(f"Model saved to {final_model_path}")
    
    # Log model to MLflow
    # Note: We are logging the PEFT adapter
    mlflow.transformers.log_model(
        transformers_model={"model": trainer.model, "tokenizer": tokenizer},
        artifact_path="model",
        input_example="<start_of_turn>user\nTest prompt<end_of_turn>\n<start_of_turn>model\n",
    )
    
    return final_model_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", type=str, required=True, help="Path to dataset_finetune.jsonl")
    parser.add_argument("--output-dir", type=str, default="model_output")
    parser.add_argument("--model-name", type=str, default="google/functiongemma-270m-it")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--experiment-name", type=str, default=None, help="MLflow experiment name for standalone run")
    args = parser.parse_args()

    # MLflow auto-logging is powerful for transformers
    mlflow.transformers.autolog()
    
    if args.experiment_name:
        mlflow.set_experiment(args.experiment_name)

    active_run = mlflow.active_run()
    if active_run:
        print(f"Attach to existing run: {active_run.info.run_id}")
    else:
        print("Starting new MLflow run...")
        mlflow.start_run(run_name="finetuning")
        
    try:
        run_finetuning(
            args.dataset_path, 
            args.output_dir, 
            args.model_name, 
            args.epochs, 
            args.batch_size, 
            args.learning_rate
        )
    finally:
        if not active_run:
            mlflow.end_run()

if __name__ == "__main__":
    main()
