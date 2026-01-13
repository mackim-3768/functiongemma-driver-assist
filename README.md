# FunctionGemma 기반 운전자 보조 데모 애플리케이션

## 1. 프로젝트 개요

본 프로젝트는 **FunctionGemma**를 활용하여, 운전자 보조 시스템에서 자연어 기반 입력이 어떻게 **구조화된 차량 기능 트리거(Function Call)** 로 변환되는지를 시연하기 위한 데모 애플리케이션입니다.

이 데모의 목적은 LLM이 직접 판단하거나 운전을 수행하는 것이 아니라,
**"어떤 차량 기능을 호출해야 하는가"를 선택하는 역할만 수행**함을 명확히 보여주는 것입니다.

---

## 2. 데모 컨셉 요약

* 사용자 관점: **조수석에 탑승한 관찰자 시점**
* 입력 방식: 자연어 프롬프트 또는 시나리오 버튼
* 핵심 역할: FunctionGemma는 판단이 아닌 **Function Selection**만 수행
* 출력 결과: 차량 액션 트리거(JSON 형태)

---

## 3. UI 구성 개요

### 3.1 메인 화면 (조수석 시야)

* 차량 전면 시야 기반 UI
* HUD / 계기판 스타일 상태 표시
* Function Call 발생 시 시각적 피드백 제공

### 3.2 좌측 시나리오 패널

사전 정의된 시나리오 버튼을 통해 즉시 테스트 가능

예시:

* 차선 이탈 경고 시나리오
* 졸음 운전 감지 시나리오
* 핸들 미그립 상태 시나리오

버튼 클릭 시 프롬프트 입력창에 자동 반영

### 3.3 하단 프롬프트 입력 영역

* 자연어 기반 입력
* FunctionGemma 호출 트리거
* Engineer Mode 활성화 시 Function Call JSON 출력

---

## 4. 시스템 아키텍처 개념

```
[ User Prompt / Scenario Button ]
              │
              ▼
       FunctionGemma
              │
     (Function Selection)
              │
              ▼
     Vehicle Action Trigger
              │
              ▼
      Mock Vehicle System
```

※ FunctionGemma는 판단/추론/책임을 가지지 않으며,
오직 **어떤 액션을 호출할지 선택**만 수행합니다.

---

## 5. 입력 Tool 정의 (Context / AI Result)

FunctionGemma에 제공되는 입력은 모두 **구조화된 상태 정보**입니다.

### 주요 Input Tool 예시

* get_lane_departure_status

  * departed: boolean
  * confidence: number

* get_driver_drowsiness_status

  * drowsy: boolean
  * confidence: number

* get_steering_grip_status

  * hands_on: boolean

* get_vehicle_speed

* get_forward_collision_risk

* get_driving_environment

* get_driving_duration_status

* get_recent_warning_history

* get_sensor_health_status

입력 Tool은 **판단을 위한 데이터 제공 목적**이며,
FunctionGemma가 직접 해석하거나 위험도를 계산하지 않습니다.

---

## 6. 출력 Tool 정의 (Vehicle Action Trigger)

FunctionGemma의 출력은 항상 **명확한 차량 액션 트리거**입니다.

### 주요 Output Tool 예시

* trigger_steering_vibration
* trigger_navigation_notification
* trigger_drowsiness_alert_sound
* trigger_cluster_visual_warning
* trigger_hud_warning
* trigger_voice_prompt
* escalate_warning_level
* trigger_rest_recommendation
* log_safety_event
* request_safe_mode

출력 Tool은 실제 차량 제어가 아닌 **Mock Vehicle System**으로 전달됩니다.

---

## 7. 대표 시나리오 예시

### 입력 상태

* 차선 이탈 감지: true (70%)
* 졸음 감지: true (80%)
* 핸들 그립: false

### FunctionGemma 출력

```json
[
  {
    "name": "trigger_steering_vibration",
    "arguments": { "intensity": "high" }
  },
  {
    "name": "trigger_navigation_notification",
    "arguments": {
      "message": "졸고 계신가요?",
      "level": "critical"
    }
  },
  {
    "name": "trigger_drowsiness_alert_sound",
    "arguments": { "volume_percent": 100 }
  }
]
```

---

## 8. 설계 원칙 (중요)

* FunctionGemma는 **결정 엔진이 아님**
* 판단 로직은 Rule Engine 또는 차량 시스템에 존재
* 출력은 항상 검증 가능한 JSON
* 온디바이스 실행을 전제로 한 소형 모델 활용

---

## 9. 데모 앱의 목적

* LLM 기반 Agent와 Function Selection 모델의 차이 명확화
* 자동차 / 임베디드 / 인증 환경에서의 현실적인 AI 적용 사례 제시
* PM, 엔지니어, 인증 담당자 모두가 이해 가능한 구조 제공

---

## 10. 향후 확장 아이디어

* Rule Engine 연동 데모
* 경고 단계 에스컬레이션 시각화
* ISO / KTC 인증 관점 로그 포맷 추가
* 실제 차량 API 연동 (PoC 단계)

---

## 11. License

This project is a demo application for research and demonstration purposes only.


## 12. 로컬 설정 파일 적용 방법

1) /data/local/tmp/.../application.yaml 정확한 경로
  - 코드(AppConfigLoader.readConfigText) 기준으로 오버라이드 1순위 경로는 고정입니다.
  - 정확한 경로: /data/local/tmp/functiongemma/application.yaml

2) 참고로 로딩 우선순위는 아래 순서입니다.
  - 1순위: /data/local/tmp/functiongemma/application.yaml
  - 2순위: /storage/emulated/0/Android/data/com.functiongemma.driverassist/files/application.yaml (=getExternalFilesDir(null))
  - 3순위: 앱 internal files (/data/data/.../files/application.yaml, adb로 접근 어려움)
  - 마지막: assets/application.yaml

3) adb로 넣는 방법
  - [디렉토리 생성] : adb shell mkdir -p /data/local/tmp/functiongemma
  - [파일 푸시] : adb push local.application.yaml /data/local/tmp/functiongemma/application.yaml
  - [확인] : adb shell ls -l /data/local/tmp/functiongemma/application.yaml


## 13. adb logcat에서 보는 방법

1) Tag로만 필터링

```bash
adb logcat -s FunctionGemmaDriverAsst
```

2) 시간 포함 + Info 이상만

```bash
adb logcat -v time FunctionGemmaDriverAsst:I *:S
이제 앱 실행 중에 config.sources selected=... 로그로 실제로 /data/local/tmp/...를 읽고 있는지 바로 확인 가능합니다.
```