import argparse
import os
import mlflow
from datasets import load_dataset
from trl import SFTTrainer
from utils.finetune_utils import (
    load_model_and_tokenizer,
    get_lora_config,
    get_data_collator,
    get_training_args
)

def run_finetuning(dataset_path, output_dir, model_name, epochs, batch_size, learning_rate):
    # 1. Load Model & Tokenizer
    model, tokenizer = load_model_and_tokenizer(model_name)
    
    # 2. Load Dataset
    print(f"Loading dataset from {dataset_path}...")
    dataset = load_dataset("json", data_files=dataset_path, split="train")

    # 3. Get LoRA Config (Optimized from train_unsloth.py)
    peft_config = get_lora_config()
    
    # 4. Get Data Collator (Fixes padding issue)
    collator = get_data_collator(tokenizer)

    # 5. Get Training Args (Stable settings)
    training_args = get_training_args(
        output_dir=output_dir,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate
    )

    # 6. Initialize Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        processing_class=tokenizer,
        args=training_args,
        peft_config=peft_config,
        data_collator=collator,
    )

    print("Starting training...")
    trainer.train()
    
    # 7. Save Model
    final_model_path = os.path.join(output_dir, "final_model")
    trainer.save_model(final_model_path)
    print(f"Model saved to {final_model_path}")
    
    # 8. Log to MLflow
    # Log the PEFT adapter
    mlflow.transformers.log_model(
        transformers_model={"model": trainer.model, "tokenizer": tokenizer},
        artifact_path="model",
        input_example="<start_of_turn>user\nTest prompt<end_of_turn>\n<start_of_turn>model\n",
    )
    
    return final_model_path

def main():
    print("Script started...")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", type=str, required=True, help="Path to dataset_finetune.jsonl")
    parser.add_argument("--output-dir", type=str, default="model_output")
    parser.add_argument("--model-name", type=str, default="google/functiongemma-270m-it")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=6)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--experiment-name", type=str, default=None, help="MLflow experiment name for standalone run")
    args = parser.parse_args()

    # MLflow auto-logging
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
