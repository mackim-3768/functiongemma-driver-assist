# FunctionGemma Driver Assist Fine-tuning

이 디렉토리는 FunctionGemma(2B) 모델을 운전자 보조 시나리오에 맞춰 파인튜닝하기 위한 스크립트를 포함합니다.

## 1. 구성 요소

*   `dataset_gen.py`: 규칙 기반으로 Context-Action 쌍을 생성하여 `driver_assist_finetune.jsonl` 데이터셋을 만듭니다.
*   `train.py`: Unsloth 라이브러리를 사용하여 LoRA 파인튜닝을 수행하고 GGUF로 내보냅니다.
*   `requirements.txt`: 필요한 라이브러리 목록입니다.

## 2. 실행 방법 (Google Colab 권장)

로컬 머신에 NVIDIA GPU가 없다면 Google Colab(무료 T4 GPU) 사용을 권장합니다.

1.  **데이터셋 생성**
    ```bash
    python dataset_gen.py
    ```
    `driver_assist_finetune.jsonl` 파일이 생성됩니다.

2.  **Colab 환경 설정**
    Colab 노트북을 열고 다음 셀을 실행하여 의존성을 설치합니다.
    ```python
    !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
    !pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes
    ```

3.  **학습 스크립트 실행**
    `train.py`와 `driver_assist_finetune.jsonl`을 Colab에 업로드한 후 실행합니다.
    ```bash
    python train.py
    ```

4.  **결과물 확인**
    `functiongemma-driver-assist-lora-unsloth.Q8_0.gguf` 파일이 생성됩니다.

## 3. 앱 적용 방법

1.  생성된 `.gguf` 파일을 Android 기기의 `/data/local/tmp/functiongemma/` 또는 앱 데이터 폴더에 복사합니다.
2.  앱의 'Function Selector' 패널에서 해당 GGUF 경로를 입력하고 LLM 모드를 활성화합니다.
