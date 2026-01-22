## application-develop.md

이 문서는 `concept/applicaiton-conecept.md`의 아키텍처(“Context Polling → Gate → FunctionGemma → Action Dispatch”)를 **현재 Android 앱 코드 구조에 자연스럽게 녹여서 구현**하기 위한 개발 시나리오를 정리합니다.

---

## 0) 현재 앱 상태(코드 기준) 요약

현재 앱은 이미 데모에 필요한 핵심 골격을 갖고 있습니다.

- `DriverAssistViewModel`
  - 데모 컨텍스트(`DriverAssistContext`)를 상태로 보유
  - `run()`에서 `FunctionSelector.select(context, prompt)` 호출 → `VehicleAction` 리스트 획득
  - `MockVehicleSystem.apply(previousState, actions)`로 실행(로그/상태 갱신)
  - LLM 사용 시 `LlamaCppFunctionSelector`로 대체 가능
- `DriverAssistApp` (Compose)
  - `InputToolsPanel`: 컨텍스트를 UI에서 직접 변경(= 데모용 override)
  - `ScenarioPanel`: 프리셋 시나리오
  - `PromptBar`: 수동 실행 버튼
  - `Engineer Mode`: 모델 출력 JSON 표시
  - `Mock Vehicle Log`: 실행 로그

즉, 지금 구조는 이미 **Manual Mode(수동 run)** 중심으로 동작합니다.

---

## 1) 목표 아키텍처를 “현재 코드에 맞게” 재해석

`concept/applicaiton-conecept.md`의 제안 구조를 현재 코드에 맞추면 다음으로 매핑됩니다.

- **ContextProvider**
  - 현재: `DriverAssistViewModel.context` + `InputToolsPanel`의 UI 토글/슬라이더
  - 확장: 실제 센서/시뮬레이터에서 주기적으로 값 갱신 + JSON 스냅샷 생성

- **ScenarioGate(Rule-based)**
  - 현재: 없음(사용자가 직접 시나리오/프롬프트로 유도)
  - 확장: 컨텍스트 스냅샷에서 “발생 여부”를 먼저 판정해서 필요할 때만 LLM 호출

- **FunctionGemmaAdapter**
  - 현재: `FunctionSelector` 인터페이스(`StubFunctionSelector` / `LlamaCppFunctionSelector`)
  - 확장: `scenario_event + context_snapshot`을 포함하는 프롬프트 구성

- **ActionDispatcher + SafetyGate**
  - 현재: `MockVehicleSystem.apply()`가 바로 action을 처리
  - 확장: `SafetyGate`에서 쿨다운/에스컬레이션/파라미터 안전성 검증 후 `MockVehicleSystem`에 전달

---

## 2) 구현 모드 2개로 나누기(권장)

### A. Manual Mode (현재 유지)

- 사용자가 컨텍스트를 조작하고 `run()`을 눌러 LLM/Stub 결과를 실행
- 데모의 “관찰 + 디버깅”에 매우 유리

### B. Auto Mode (추가 구현)

- `ContextProvider`가 주기적으로 `ContextSnapshot`을 업데이트
- `ScenarioGate`가 “발생”일 때만 LLM을 호출
- `SafetyGate + Dispatcher`가 실행 여부를 최종 판단

Auto Mode는 **기존 UI 흐름을 깨지 않고**, 토글 하나로 활성화/비활성화 가능해야 합니다.

---

## 3) 추천 데이터 모델(현 모델과의 연결)

현재는 `DriverAssistContext`가 “일부 컨텍스트(6개)”만 포함합니다.
`context_tool.json`(10개)을 반영하려면 스냅샷 계층을 하나 더 두는 편이 안전합니다.

### 3.1 ContextSnapshot (권장)

- 역할: “LLM에 입력할 최신 상태”를 1개의 JSON으로 보존
- 형태: `JSONObject` 또는 `Map<String, Any>`

권장 키 구조(툴 이름 기준):
- `get_lane_departure_status`: `{ departed, confidence }`
- `get_driver_drowsiness_status`: `{ drowsy, confidence }`
- `get_steering_grip_status`: `{ hands_on }`
- `get_vehicle_speed`: `{ speed_kph }`
- `get_lka_status`: `{ enabled }`
- `get_forward_collision_risk`: `{ risk_score, risk_level }`
- `get_driving_environment`: `{ weather, road_condition, visibility }`
- `get_driving_duration_status`: `{ driving_minutes, fatigue_risk }`
- `get_recent_warning_history`: `{ last_warning_type, seconds_ago }`
- `get_sensor_health_status`: `{ camera_ok, ai_model_confidence }`

### 3.2 ScenarioEvent (권장)

- Enum으로 관리하는 것을 추천
- 예시:
  - `LANE_DEPARTURE_HIGH_SPEED`
  - `DROWSY_CONFIDENT`
  - `DROWSY_NO_HANDS`
  - `FORWARD_COLLISION_HIGH`
  - `SENSOR_HEALTH_LOW`

### 3.3 ActionCall / VehicleAction

현재는 `VehicleAction(name, arguments)`로 충분히 표현 가능합니다.
`action_tool.json`의 `tool_call_format`과 1:1 매핑됩니다.

---

## 4) ContextProvider 구현 시나리오

### 4.1 1단계(최소 변경): 기존 UI override를 ContextProvider로 간주

- `InputToolsPanel`에서 조작되는 `DriverAssistViewModel.context`를 “센서 값”이라고 보고
- `ContextSnapshot`으로 변환하는 함수만 추가(또는 Adapter에서 즉석 생성)

이 단계에서는 실제 폴링 없이도 Gate/LLM/Dispatcher 분리가 가능합니다.

### 4.2 2단계(자동화): Polling Loop 추가

- 위치: `DriverAssistViewModel` 내부(또는 별도 `ContextProvider` 클래스)
- 구현: `viewModelScope.launch { while(autoMode) { updateSnapshot(); delay(...) } }`
- 권장 주기: 100~200ms(5~10Hz)

데모에서는 “실 센서”가 없으므로 다음 중 하나를 선택합니다.
- **Option 1**: 폴링하지만 값은 UI에서 바뀐 값을 그대로 읽어 snapshot 구성
- **Option 2**: 간단한 시뮬레이터(랜덤/패턴)로 값을 조금씩 변화

---

## 5) ScenarioGate 구현 시나리오

`ScenarioGate`는 **LLM 호출을 줄이기 위한 1차 필터**입니다.

### 5.1 추천 Rule Set(컨셉 문서 기반)

- `DROWSY_NO_HANDS`
  - `drowsy == true && confidence >= 0.8 && hands_on == false`
- `LANE_DEPARTURE_HIGH_SPEED`
  - `departed == true && confidence >= 0.7 && speed_kph >= 60`
- `FORWARD_COLLISION_HIGH`
  - `risk_level == "high" && risk_score >= 0.75`

### 5.2 출력(권장)

Gate 결과는 단순 Boolean이 아니라, 디버깅을 위해 다음을 포함하는 것을 권장합니다.
- `triggered: Boolean`
- `event: ScenarioEvent?`
- `reason: String` (왜 발동했는지)

이 `reason`은 오른쪽 Engineer Console(현재는 `Mock Vehicle Log` 영역)에도 노출하면 데모 신뢰도가 크게 올라갑니다.

---

## 6) FunctionGemmaAdapter(= LlamaCppFunctionSelector 확장 방향)

현재 `LlamaCppFunctionSelector.buildPrompt(context, userPrompt)`는 `DriverAssistContext`만 넣습니다.
Auto Mode에서는 최소 아래를 포함하도록 확장하는 것이 좋습니다.

- `scenario_event`: Gate가 만든 사건
- `context_snapshot`: 최신 스냅샷(JSON)
- `cooldown_hint`(선택): 최근 경고 이력/쿨다운 정보를 힌트로 제공

### 6.1 프롬프트 구성 원칙

- 출력은 **무조건 JSON array만**
- “정의된 tool name만 허용”
- “추가 텍스트/설명 금지”

현재 `LlamaCppFunctionSelector`가 이미 이 방향으로 구현되어 있어(“Return ONLY a JSON array…”) 컨셉과 잘 맞습니다.

### 6.2 action_tool.json 동기화(권장)

현재는 prompt에 허용 tool 이름이 하드코딩되어 있습니다.
데모 유지보수성을 위해 다음 중 하나를 추천합니다.

- **Option 1**: `action_tool.json`을 읽어 tool name 목록을 prompt에 주입
- **Option 2**: 최소한 tool name 목록을 단일 상수로 모으고(`tools`와 prompt에서 공유)

---

## 7) SafetyGate + ActionDispatcher 구현 시나리오

현재 `MockVehicleSystem.apply()`가 바로 실행을 수행합니다.
이를 아래처럼 2단으로 쪼개면 컨셉에 부합합니다.

1) `SafetyGate.filter(previousState, actions, snapshot)`
- 결과: `executedActions`, `blockedActions(with reason)`

2) `ActionDispatcher.dispatch(executedActions)`
- 데모에서는 `MockVehicleSystem.apply()` 호출로 충분

### 7.1 SafetyGate에서 다룰 최소 규칙(데모용)

- **쿨다운**
  - 같은 타입 경고는 N초 내 재실행 금지
- **레벨 에스컬레이션 일관성**
  - `critical`은 최근 `warning`/`critical` 이력과 함께만 허용(또는 Gate 이벤트가 강할 때만)
- **파라미터 안전성**
  - 예: `trigger_drowsiness_alert_sound.volume_percent`는 0~100 강제

이 레이어를 두면, 모델이 실수해도 “실행 단계에서 안전하게 보정/차단”이 가능합니다.

---

## 8) ViewModel에 붙이는 “실행 흐름” 제안

### 8.1 Manual Mode 흐름(현재)

- UI 조작 → `context/prompt` 변경 → `run()`
- `FunctionSelector.select()`
- `MockVehicleSystem.apply()`

### 8.2 Auto Mode 흐름(추가)

- Auto Mode ON
- Poll loop가 `ContextSnapshot`을 갱신
- 매 tick마다:
  - `ScenarioGate.evaluate(snapshot)`
  - `triggered == true`일 때만 `FunctionSelector.select()` 호출
  - 결과 action을 `SafetyGate`로 필터링
  - `MockVehicleSystem.apply()`로 실행

Auto Mode에서도 “LLM 호출 빈도 제한(예: 최소 1~2초 간격)”을 별도로 두는 것을 추천합니다.

---

## 9) UI(Compose) 확장 포인트(최소 변경)

현재 UI에 이미 필요한 대부분이 있으므로, 추가는 최소가 좋습니다.

- `Auto Mode` 토글 추가
- `Cooldown 상태 표시` (예: “drowsiness alert: cooldown 7s”)
- `ScenarioGate reason 표시` (왜 발동했는지)
- `SafetyGate 결과 표시` (Executed/Blocked + reason)

현재 `Engineer Mode` 영역을 확장해서
- `Latest ContextSnapshot JSON`
- `Gate decision`
- `LLM raw output JSON`
- `SafetyGate report`
를 같이 보여주면 컨셉 문서의 “Engineer Console”에 가깝게 구현됩니다.

---

## 10) 단계별 개발 플랜(추천)

- 1단계: 코드 구조 분리
  - `ScenarioGate` 추가
  - `SafetyGate` 추가
  - 기존 `run()`을 “Gate/Selector/Safety/Dispatch” 파이프라인 형태로 리팩터링(동작 동일)

- 2단계: Auto Mode(폴링) 추가
  - `autoModeEnabled` 상태 + polling job
  - Gate가 trigger일 때만 LLM 호출

- 3단계: JSON 스펙 연동 강화
  - `action_tool.json` 기반 tool 목록 동기화
  - (선택) action arguments 검증 강화

- 4단계: 데모 UX 강화
  - 쿨다운/차단 사유 표시
  - 로그 뷰 정리

---

## 11) 테스트/검증 포인트(데모 품질용)

- `ScenarioGate` 단위 테스트
  - 특정 snapshot 입력 → event/reason 기대값
- `SafetyGate` 단위 테스트
  - 쿨다운/레벨 보정/파라미터 clamp 검증
- “LLM 출력 파서” 견고성 테스트
  - 현재 `LlamaCppFunctionSelector`는 JSON array 추출/태그 추출까지 방어 로직이 있으므로 유지

---

## 12) 결론

현재 앱은 이미 “컨텍스트/프롬프트 → 함수 선택 → 액션 실행/로그”의 기본 구조가 갖춰져 있어,
`Context Polling`과 `ScenarioGate`, `SafetyGate`를 **ViewModel 중심으로 얹기만 하면** 컨셉 문서의 아키텍처를 자연스럽게 구현할 수 있습니다.
