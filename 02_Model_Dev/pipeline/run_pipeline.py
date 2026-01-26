import argparse
import os
import shutil
import mlflow
from datetime import datetime

# Import step functions
from step1_generate_data import run_generator
from step2_finetune import run_finetuning
from step3_evaluate import run_evaluation

def main():
    parser = argparse.ArgumentParser(description="Driver Assist Function Gemma Pipeline")
    parser.add_argument("--experiment-name", type=str, default="driver_assist_function_gemma")
    parser.add_argument("--base-output-dir", type=str, default="pipeline_outputs")
    
    # Gen Params
    parser.add_argument("--gen-samples", type=int, default=100)
    parser.add_argument("--gen-seed", type=int, default=42)
    
    # Train Params
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--base-model", type=str, default="google/functiongemma-270m-it")
    
    # Eval Params
    parser.add_argument("--geval", action="store_true", help="Enable OpenAI G-Eval judging")
    parser.add_argument("--geval-model", type=str, default="gpt-4o-mini")
    parser.add_argument("--geval-max-samples", type=int, default=0, help="0 means judge all samples")
    
    args = parser.parse_args()
    
    # Setup Output Dir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(args.base_output_dir, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"🚀 Starting Pipeline... Output: {run_dir}")
    
    # Initialize Pipeline Context
    from chatbot_tester.utils import PipelineContext
    
    with PipelineContext(args.experiment_name, args.base_output_dir) as ctx:
        ctx.log_params({
            "base_model": args.base_model,
            "gen_samples": args.gen_samples
        })
        
        # --- Step 1: Generation ---
        with ctx.step("data_generation") as step1_dir:
            print("\n[Step 1] Data Generation")
            
            c_path, f_path, m_path, meta = run_generator(
                output_dir=step1_dir,
                num_samples=args.gen_samples,
                seed=args.gen_seed
            )
            
            # Log artifacts
            # Note: PipelineContext.log_artifact logs to current active run (which is step run here)
            ctx.log_artifact(c_path)
            ctx.log_artifact(f_path)
            ctx.log_artifact(m_path)
            
            # Log tags
            mlflow.set_tag("dataset_version", meta["version"])
            for tag, count in meta["tag_stats"].items():
                mlflow.log_metric(f"count_{tag}", count)

        # --- Step 2: Fine-tuning ---
        with ctx.step("finetuning") as step2_dir:
            print("\n[Step 2] Fine-tuning")
             
            # HF Autolog setup
            mlflow.transformers.autolog()
             
            model_path = run_finetuning(
                 dataset_path=f_path,
                 output_dir=step2_dir,
                 model_name=args.base_model,
                 epochs=args.epochs,
                 batch_size=args.batch_size,
                 learning_rate=args.lr
            )
             
        # --- Step 3: Evaluation ---
        with ctx.step("evaluation") as step3_dir:
            print("\n[Step 3] Evaluation")
            
            metrics, res_path, geval_path = run_evaluation(
                model_path=model_path,
                dataset_path=c_path,
                base_model_name=args.base_model,
                output_dir=step3_dir,
                enable_geval=args.geval,
                geval_model=args.geval_model,
                geval_max_samples=args.geval_max_samples,
            )
            
            # Log metrics
            ctx.log_metrics(metrics)
            ctx.log_artifact(res_path)

            if geval_path:
                ctx.log_artifact(geval_path)
            
            # Check Threshold
            if metrics["accuracy_total"] < 0.8:
                print("⚠️ Warning: Model accuracy is below 80%")
                mlflow.set_tag("status", "failed_threshold")
            else:
                mlflow.set_tag("status", "passed")
                
    print(f"\n✅ Pipeline Complete! Check MLflow for results.")

if __name__ == "__main__":
    main()
