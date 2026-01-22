                                # Driver Assist Function Gemma Pipeline

This pipeline automates the process of generating synthetic data, fine-tuning Function Gemma, and evaluating the result, all tracked via MLflow.

## Structure

- `step1_generate_data.py`: Generates synthetic data using the `chatbot-tester` compatible logic. Produces canonical dataset (for eval) and finetuning dataset.
- `step2_finetune.py`: Fine-tunes `google/functiongemma-270m-it` (or other models) using LoRA/QLoRA.
- `step3_evaluate.py`: Evaluates the fine-tuned model against the canonical dataset and calculates accuracy.
- `run_pipeline.py`: Master orchestrator that runs all steps in sequence within a nested MLflow run.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Ensure `chatbot-tester` is present in `../chatbot-tester`.*

2. Configure MLflow (Optional):
   By default, it logs to local `./mlruns`. Set `MLFLOW_TRACKING_URI` if needed.

## Usage

Run the full pipeline:

```bash
python run_pipeline.py \
  --experiment-name "driver_assist_v1" \
  --gen-samples 500 \
  --epochs 3
```

### Arguments

- `--gen-samples`: Number of synthetic samples to generate (default: 100).
- `--gen-seed`: Random seed for generation.
- `--epochs`: Training epochs.
- `--base-model`: Hugging Face model ID (default: `google/functiongemma-270m-it`).

## Outputs

Artifacts are stored in `pipeline_outputs/run_<timestamp>/` and logged to MLflow.

- `step1_data/`: `dataset_canonical.jsonl`, `dataset_finetune.jsonl`, `metadata.json`
- `step2_model/`: Saved Peft adapter.
- `step3_eval/`: `eval_results.json`.

## MLflow Tracking

Open MLflow UI to view results:

```bash
mlflow ui
```

You will see:
- **Parent Run**: Pipeline overview.
- **Child Runs**:
  - `data_generation`: Parameters, dataset stats.
  - `finetuning`: Training loss curves, model parameters.
  - `evaluation`: Accuracy metrics, validation results.
