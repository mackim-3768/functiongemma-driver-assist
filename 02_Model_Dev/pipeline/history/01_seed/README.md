# 🚗 Driver Assist Seed Dataset (v1.0)

## 📌 Overview
이 데이터셋은 **Function Gemma** 모델이 운전자 보조 시스템(Driver Assist) 도메인의 함수 호출(Function Calling)을 학습할 수 있는지 **가능성을 검증(Feasibility Test)** 하기 위해 생성된 초기 Seed 데이터셋입니다.

## 📊 Data Statistics
*   **Total Samples**: 1000
*   **Train Set**: 900 (90.0%)
*   **Eval Set**: 100 (10.0%)

### 🏷️ Scenario Distribution
다양한 운전 상황 시나리오가 포함되어 있으며, 분포는 다음과 같습니다.

| Scenario Tag | Count | Percentage |
| :--- | :--- | :--- |
| `normal` | 209 | 20.9% |
| `safe_mode_needed` | 205 | 20.5% |
| `collision_risk` | 113 | 11.3% |
| `lane_departure` | 105 | 10.5% |
| `sensor_fail` | 102 | 10.2% |
| `complex` | 100 | 10.0% |
| `hands_off` | 92 | 9.2% |
| `bad_weather` | 74 | 7.4% |

## 🎯 Purpose
1.  **Baseline Performance Check**: 기본적인 9가지 시나리오(졸음, 차선이탈 등)에 대해 모델이 올바른 JSON 포맷으로 도구를 호출하는지 확인.
2.  **Metric Setup**: Accuracy, JSON Validity 등 평가 지표 파이프라인이 정상 동작하는지 테스트.
3.  **Overfitting Test**: 소규모 데이터셋으로 파인튜닝 시 모델이 의도한 대로 행동을 교정하는지 확인.

## 📂 File Structure
*   `train_finetune.jsonl`: 학습용 데이터 (Function Gemma Format)
*   `eval_canonical.jsonl`: 평가용 데이터 (Ground Truth 포함, Chatbot Tester Format)
*   `eval_finetune.jsonl`: 학습 중 Loss 계산용 (Optional)

## 🚀 Usage
이 데이터셋은 `02_Model_Dev/pipeline` 의 `step2_finetune.py` 와 `step3_evaluate.py` 에서 즉시 사용할 수 있습니다.
