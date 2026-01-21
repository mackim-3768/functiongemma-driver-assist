# FunctionGemma Driver Assist Fine-tuning (270M)

이 디렉토리는 `google/functiongemma-270m-it` 모델을 운전자 보조 시나리오에 맞춰 파인튜닝하기 위한 스크립트를 포함합니다.

## 1. 구성 요소

*   `dataset_gen.py`: 규칙 기반으로 Context-Action 쌍을 생성하여 `driver_assist_finetune.jsonl` 데이터셋을 만듭니다.
*   `train.py`: Hugging Face `transformers`와 `peft`를 사용하여 LoRA 파인튜닝을 수행하고, 병합된 모델을 저장합니다.
*   `requirements.txt`: 필요한 라이브러리 목록입니다.
*   `train_unsloth.py`: (구버전) Unsloth 기반 2B 모델 학습 스크립트.

## 2. 실행 방법

### 환경 설정
```bash
pip install -r requirements.txt
```

### 학습 실행
```bash
python train.py
```
학습이 완료되면 `merged_functiongemma-270m-driver-assist` 폴더에 HF 포맷의 모델이 저장됩니다.

## 3. GGUF 변환 (llama.cpp 필요)

모바일 기기에서 실행하기 위해 GGUF 포맷으로 변환해야 합니다. [llama.cpp](https://github.com/ggerganov/llama.cpp)가 필요합니다.

1.  **llama.cpp 클론 및 설치**
    ```bash
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp
    pip install -r requirements.txt
    ```

2.  **변환 실행**
    ```bash
    # finetune 디렉토리에서 실행한다고 가정
    python ../llama.cpp/convert_hf_to_gguf.py merged_functiongemma-270m-driver-assist --outfile functiongemma-270m-it-driver-assist.gguf
    ```
    (경로는 실제 llama.cpp 위치에 맞게 조정하세요)

3.  **(선택사항) 양자화**
    모델 사이즈를 더 줄이려면 양자화를 수행합니다.
    ```bash
    ./llama-quantize functiongemma-270m-it-driver-assist.gguf functiongemma-270m-it-driver-assist-q8_0.gguf q8_0
    ```

## 4. 앱 적용 방법

1.  생성된 `.gguf` 파일을 Android 기기의 `/data/local/tmp/functiongemma/` 또는 앱 데이터 폴더에 복사합니다.
2.  앱의 'Function Selector' 패널에서 해당 GGUF 경로를 입력하고 LLM 모드를 활성화합니다.
