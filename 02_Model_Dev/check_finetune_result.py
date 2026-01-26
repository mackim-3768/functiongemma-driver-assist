
import json
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from tqdm import tqdm

# --- 설정 (경로 수정 필요 시 여기를 변경하세요) ---
BASE_MODEL_NAME = "google/functiongemma-270m-it"
# 파인튜닝 결과물 (LoRA 어댑터) 경로
ADAPTER_PATH = "./pipeline/history/01_seed/run_v5/test_finetune_output/final_model"
# 테스트할 데이터셋 경로
DATA_PATH = "./pipeline/history/01_seed/eval_canonical.jsonl"
# 결과 저장 파일
OUTPUT_FILE = "comparison_report.txt"

# Mac(MPS) 이슈 방지를 위해 CPU/Float32 강제 사용
DEVICE = "cpu"
DTYPE = torch.float32

def load_base_model(model_name):
    print(f"Loading Base Model: {model_name} on {DEVICE}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=DTYPE,
        device_map=DEVICE,
        trust_remote_code=True
    )
    return model, tokenizer

def run_inference(model, tokenizer, prompt):
    # 데이터셋의 불필요한 태그 제거
    cleaned_prompt = prompt.replace("<end_of_turn>", "").strip()
    
    # Gemma 프롬프트 포맷 적용
    # tokenizer.bos_token이 설정 안 된 경우 대비
    bos = tokenizer.bos_token if tokenizer.bos_token else "<bos>"
    formatted_prompt = f"{bos}<start_of_turn>user\n{cleaned_prompt}<end_of_turn>\n<start_of_turn>model\n"
    
    inputs = tokenizer(
        formatted_prompt, 
        return_tensors="pt", 
        add_special_tokens=False
    ).to(model.device)
    
    # 종료 조건 설정
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<end_of_turn>")
    ]
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False, # 결정론적 결과 (Greedy Decoding)
            eos_token_id=terminators,
        )
    
    # 입력 프롬프트 제외하고 생성된 답변만 추출
    input_len = inputs.input_ids.shape[1]
    generated_ids = outputs[0][input_len:]
    response = tokenizer.decode(generated_ids, skip_special_tokens=True)
    
    return response.strip()

def main():
    if not os.path.exists(ADAPTER_PATH):
        print(f"Error: Adapter path not found: {ADAPTER_PATH}")
        return
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data path not found: {DATA_PATH}")
        return

    print(f"Reading data from {DATA_PATH}")
    with open(DATA_PATH, "r") as f:
        # 테스트 시간을 위해 앞쪽 3개 샘플만 사용 (전체 실행하려면 슬라이싱 제거)
        samples = [json.loads(line) for line in f][:3]

    # 1. Base Model 실행
    print("\n" + "="*50)
    print("Phase 1: Running Base Model (Before Finetuning)")
    print("="*50)
    model, tokenizer = load_base_model(BASE_MODEL_NAME)
    
    results = []
    for sample in tqdm(samples, desc="Base Model Inference"):
        user_msg = next((m["content"] for m in sample["messages"] if m["role"] == "user"), "")
        base_output = run_inference(model, tokenizer, user_msg)
        
        # 긴 프롬프트 요약 (화면 표시용)
        try:
            short_prompt = user_msg.split("User prompt:\n")[-1].split("\n\nReturn")[0].strip()
        except:
            short_prompt = "Context..."

        results.append({
            "id": sample["id"],
            "input": short_prompt,
            "full_input": user_msg,
            "expected": json.dumps(sample["expected"], indent=2),
            "base_output": base_output
        })

    # 2. Finetuned Model (Adapter) 로드 및 실행
    print("\n" + "="*50)
    print("Phase 2: Loading Adapter & Running Finetuned Model")
    print("="*50)
    print(f"Loading Adapter from {ADAPTER_PATH}")
    model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    model.to(DEVICE)
    model.eval()
    
    for i, sample in enumerate(tqdm(samples, desc="Finetuned Model Inference")):
        ft_output = run_inference(model, tokenizer, results[i]["full_input"])
        results[i]["ft_output"] = ft_output

    # 3. 결과 저장 및 출력
    print(f"\nSaving detailed comparison to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        f.write("="*80 + "\n")
        f.write("COMPARISON RESULTS (Base vs Finetuned)\n")
        f.write("="*80 + "\n")
        for res in results:
            f.write(f"\n[Sample ID: {res['id']}]\n")
            f.write(f"Input Command: {res['input']}\n")
            f.write("-" * 40 + "\n")
            f.write(f"Expected (Label):\n{res['expected']}\n")
            f.write("-" * 40 + "\n")
            f.write(f"Base Model Output:\n{res['base_output']}\n")
            f.write("-" * 40 + "\n")
            f.write(f"Finetuned Model Output:\n{res['ft_output']}\n")
            f.write("="*80 + "\n")
            
    # 화면에 간단 요약 출력
    print("\n" + "="*80)
    print("Sample Results Preview:")
    for res in results:
        print(f"\nCommand: {res['input']}")
        print(f" -> Base: {res['base_output'][:50]}...")
        print(f" -> Finetuned: {res['ft_output']}")
    print("="*80)
    print(f"\nDone! Check {OUTPUT_FILE} for full details.")

if __name__ == "__main__":
    main()
