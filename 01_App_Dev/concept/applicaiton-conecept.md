## 1) 전체 구조 제안: “Context Polling → Gate → FunctionGemma → Action Dispatch”

### 핵심 원칙

* **Context Tool은 앱이 폴링**해서 최신 스냅샷을 만든다. (FunctionGemma가 폴링하지 않음)
* **시나리오 ‘발생 여부’는 Gate(룰)로 1차 판정**하고, “발생”일 때만 FunctionGemma를 호출한다.

    * 이유: 불필요한 LLM 호출 비용/지연 감소, 오작동 리스크 감소, 디버깅 용이
* FunctionGemma의 역할은 오직 **“어떤 Action Tool을 어떤 파라미터로 트리거할지 선택”**이다.
* Action 실행은 **Dispatcher + Safety Gate**에서 최종 검증(레벨/중복/쿨다운) 후 수행한다.

### 모듈 구성(추천)

1. **ContextProvider**

    * `context_tool.json`에 정의된 10개 컨텍스트를 일정 주기로 폴링
    * 결과를 `ContextSnapshot`(단일 JSON)으로 정규화/저장
2. **ScenarioGate (Rule-based)**

    * 예: `drowsy && hands_on == false` 같은 “발생 조건”만 간단히 판정
    * 발생 시 “ScenarioEvent” 생성 (예: `DROWSY_NO_HANDS`)
3. **FunctionGemmaAdapter**

    * ScenarioEvent + ContextSnapshot을 프롬프트로 구성
    * `action_tool.json`의 스키마에 맞는 **Action Tool call array**만 출력하도록 강제
4. **ActionDispatcher**

    * JSON array를 파싱하여 Mock Vehicle System에 실행
5. **SafetyGate (Execution Safety)**

    * 중복 경고 쿨다운, 레벨 에스컬레이션 규칙, “critical일 때만 sound 100% 허용” 등
6. **UI Layer**

    * Passenger-view 메인 + 좌측 시나리오 + 하단 프롬프트 + 우측 로그/상태

---

## 2) “지속 폴링 + 특정 시나리오 발생 시 호출” 실행 흐름

### Polling Loop (예: 5~10Hz 권장)

* 100~200ms마다 ContextProvider가 아래를 최신화:

    * `get_lane_departure_status()`
    * `get_driver_drowsiness_status()`
    * `get_steering_grip_status()`
    * … (총 10개)

### ScenarioGate 예시 (당장 쓰기 좋은 형태)

* **졸음 + 손 안잡음**:

    * `drowsy == true && confidence >= 0.8 && hands_on == false`
* **차선 이탈 + 속도 고속**:

    * `departed == true && confidence >= 0.7 && speed_kph >= 60`
* **전방 충돌 high**:

    * `risk_level == "high" && risk_score >= 0.75`

발생하면 FunctionGemma에 넘길 입력은 “전체 컨텍스트”이되, **최소한 아래 2가지는 항상 포함**하세요.

* `scenario_event` (이번에 발생한 사건)
* `context_snapshot` (현재 상태 스냅샷)

---

## 3) FunctionGemma 입력/출력 포맷 추천

### 출력 스키마 (이미 파일에 정의됨)

Action Tool 출력은 **배열 형태**로 정의되어 있습니다. 즉, FunctionGemma는 아래처럼만 내보내게 만드는 게 정답입니다.

```json
[
  {"name":"trigger_steering_vibration","arguments":{"intensity":"high"}},
  {"name":"trigger_navigation_notification","arguments":{"message":"졸고 계신가요?","level":"critical"}},
  {"name":"trigger_drowsiness_alert_sound","arguments":{"volume_percent":100}}
]
```

### 프롬프트 템플릿(강제형)

데모 품질을 올리려면 시스템/유저 프롬프트를 아래처럼 “실수할 수 없는 형태”로 고정하세요.

* **System Prompt(개념)**

    * “너는 action tool call array만 출력한다”
    * “설명 금지, 텍스트 금지, JSON만”
    * “정의된 tools 외에는 호출 금지”
    * “추가 키 금지(additionalProperties=false 준수)”

* **User Prompt(실데이터)**

    * `scenario_event`
    * `context_snapshot`
    * “필요한 action을 병렬로 선택하라”
    * “중복 경고는 피하라(쿨다운 힌트)”

---

## 4) llama-cli 실행 커맨드 구성 방식 (권장)

지금 예시는 단일 tool call schema인데, 이번 데모는 **action call array**가 목표입니다. 따라서 `--json-schema`는 `action_tool.json`의 `tool_call_format`과 동일하게 맞추는 것이 가장 깔끔합니다.

### 권장 운영 방식

* `schemas/action_call_array.schema.json` 파일을 만들어 `--json-schema @파일`로 넘김
* 프롬프트는 `scenario_event + context_snapshot`을 포함한 문자열로 구성

예시 커맨드 형태:

```bash
./build/bin/llama-cli \
  -m functiongemma-270m-it.Q8_0.gguf \
  -ngl 99 --temp 0.0 -n 80 -st \
  --json-schema @schemas/action_call_array.schema.json \
  --prompt @prompts/scenario_prompt.txt
```

---

## 5) 데모 앱 UI 제안: “관찰 + 제어 + 디버깅”을 동시에 만족

### 화면 레이아웃(추천)

1. **Center (Passenger View Main)**

    * 조수석 시야의 정적 이미지/간단한 애니메이션
    * HUD 오버레이: Lane / Drowsy / HandsOn / Speed / Risk 등을 아이콘+색으로 표기
2. **Left Drawer (Scenario Panel)**

    * “Trigger Scenario” 버튼들
    * “Context Override”(데모용) 슬라이더/토글:

        * drowsy true/false + confidence 슬라이더
        * departed true/false + confidence 슬라이더
        * hands_on true/false
        * speed_kph 입력
    * 즉, 실센서가 없어도 **상태를 인위적으로 만들 수 있는 패널**
3. **Bottom (Prompt Bar)**

    * Free prompt 입력 (대화형 컨셉 유지)
    * “Auto Mode” 토글:

        * ON: Polling + Gate에 의해 자동 호출
        * OFF: 버튼/프롬프트로 수동 호출
4. **Right Panel (Engineer Console)**

    * 최근 ContextSnapshot(JSON)
    * ScenarioGate 판정 로그 (왜 발생했는지)
    * FunctionGemma raw output(JSON array)
    * ActionDispatcher 실행 로그(실행/차단/쿨다운 사유)

### UI에서 반드시 넣을 것(데모 신뢰도)

* **Auto Mode / Manual Mode** 스위치
* **쿨다운 표시(예: “drowsiness alert: cooldown 7s”)**
* **SafetyGate 결과(Executed / Blocked + reason)**

---

## 6) “컨셉 일관성”을 위해 추천하는 동작 규칙 3가지

1. **FunctionGemma는 “항상 최신 스냅샷 1개만” 보고 결정**

    * 멀티턴/연쇄추론처럼 보이지 않게 설계
2. **시나리오 발생 조건은 Rule로 단순화**

    * “발생했으니 어떤 조치를 할까”만 FunctionGemma에게 맡김
3. **실행 책임은 SafetyGate에 둔다**

    * FunctionGemma가 “sound 100%”를 내더라도,
    * 속도/이력/환경에 따라 실제 실행 강도는 SafetyGate가 조정 가능