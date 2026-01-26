# Model Development & Evaluation

This directory contains scripts for data preparation, fine-tuning, and evaluating the FunctionGemma model for the Driver Assist application.

## 🚀 Quick Start: Check Finetune Results

To verify the performance of the fine-tuned model compared to the base model, use the `check_finetune_result.py` script.

### Prerequisites
- Active virtual environment with dependencies installed.
- Fine-tuned adapter model at `./pipeline/history/01_seed/run_v5/test_finetune_output/final_model`
- Evaluation dataset at `./pipeline/history/01_seed/eval_canonical.jsonl`

### How to Run
```bash
python check_finetune_result.py
```

### What it does
1.  **Phase 1**: Runs inference using the base model (`google/functiongemma-270m-it`) on sample data.
2.  **Phase 2**: Loads your LoRA adapter and runs inference again on the same data.
3.  **Output**:
    - Prints a quick summary to the console.
    - Saves a detailed side-by-side comparison to `comparison_report.txt`.

### Troubleshooting
- **MPS (Mac) Issues**: The script is forced to use `cpu` and `float32` by default to avoid known PyTorch MPS issues with specific operations. If you want to use GPU, edit the `DEVICE` variable in the script, but be aware of potential errors.

---

## Directory Structure
- `finetune/`: Contains fine-tuning scripts (`dataset_gen_v2.py`, etc.).
- `pipeline/`: Pipeline orchestration scripts.
- `DataSet/`: Source datasets.
- `check_finetune_result.py`: **[Main Tool]** Script to compare Base vs Finetuned model outputs.
