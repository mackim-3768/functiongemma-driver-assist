import mlflow
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def retry_logging(model_path, base_model_name, experiment_name):
    print(f"Loading base model {base_model_name}...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        device_map="auto",
        trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    
    print(f"Loading adapter from {model_path}...")
    model = PeftModel.from_pretrained(model, model_path)
    
    print(f"Setting experiment to {experiment_name}...")
    mlflow.set_experiment(experiment_name)
    
    print("Starting MLflow run for logging...")
    with mlflow.start_run(run_name="finetuning_retry_logging") as run:
        print(f"Logging model to MLflow run {run.info.run_id}...")
        mlflow.transformers.log_model(
            transformers_model={"model": model, "tokenizer": tokenizer},
            artifact_path="model",
            input_example="<start_of_turn>user\nTest prompt<end_of_turn>\n<start_of_turn>model\n",
        )
        print("Done.")

if __name__ == "__main__":
    # Parameters from your previous run
    retry_logging(
        model_path="pipeline/history/01_seed/run/final_model",
        base_model_name="google/functiongemma-270m-it",
        experiment_name="driver_assist_history_run"
    )
