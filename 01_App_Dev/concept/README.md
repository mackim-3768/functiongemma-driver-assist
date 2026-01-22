# 1. 입력용 Tool 정의 (Input / Context Tools)

> 목적:
> **Function Gemma가 ‘상황을 판단하지 않고’,
> 현재 시스템 상태를 구조적으로 “받아보기”만 하기 위한 입력**

---

## Input Tool 1. 차선 이탈 감지 상태

```json
{
  "name": "get_lane_departure_status",
  "description": "Lane departure detection result",
  "arguments": {
    "departed": "boolean",
    "confidence": "number"
  }
}
```

---

## Input Tool 2. 운전자 졸음 감지 상태

```json
{
  "name": "get_driver_drowsiness_status",
  "description": "Driver drowsiness detection result",
  "arguments": {
    "drowsy": "boolean",
    "confidence": "number"
  }
}
```

---

## Input Tool 3. 핸들 그립 상태

```json
{
  "name": "get_steering_grip_status",
  "description": "Steering wheel grip detection",
  "arguments": {
    "hands_on": "boolean"
  }
}
```

---

## Input Tool 4. 차량 속도 상태

```json
{
  "name": "get_vehicle_speed",
  "description": "Current vehicle speed",
  "arguments": {
    "speed_kmh": "number"
  }
}
```

---

## Input Tool 5. 차선 유지 보조 활성 상태

```json
{
  "name": "get_lka_status",
  "description": "Lane Keep Assist active status",
  "arguments": {
    "enabled": "boolean"
  }
}
```

---

## Input Tool 6. 전방 충돌 위험 상태

```json
{
  "name": "get_forward_collision_risk",
  "description": "Forward collision risk estimation",
  "arguments": {
    "risk_level": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    }
  }
}
```

---

## Input Tool 7. 주행 환경 상태

```json
{
  "name": "get_driving_environment",
  "description": "Driving environment conditions",
  "arguments": {
    "weather": "string",
    "road_condition": "string",
    "visibility": "string"
  }
}
```

---

## Input Tool 8. 시간 기반 피로도 추정

```json
{
  "name": "get_driving_duration_status",
  "description": "Driving duration and fatigue estimation",
  "arguments": {
    "driving_minutes": "number",
    "fatigue_risk": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    }
  }
}
```

---

## Input Tool 9. 최근 경고 이력

```json
{
  "name": "get_recent_warning_history",
  "description": "Recent driver warning history",
  "arguments": {
    "last_warning_type": "string",
    "seconds_ago": "number"
  }
}
```

---

## Input Tool 10. 시스템 신뢰도 상태

```json
{
  "name": "get_sensor_health_status",
  "description": "Sensor and AI model health status",
  "arguments": {
    "camera_ok": "boolean",
    "ai_model_confidence": "number"
  }
}
```

---

# 2. 출력용 Tool 정의 (Output / Action Tools)

> 목적:
> **Function Gemma는 “무엇을 실행할지 선택”만 하고,
> 실제 실행·강도·안전 판단은 하위 시스템이 담당**

---

## Output Tool 1. 핸들 진동 트리거

```json
{
  "name": "trigger_steering_vibration",
  "description": "Trigger steering wheel vibration",
  "arguments": {
    "intensity": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    }
  }
}
```

---

## Output Tool 2. 네비게이션 경고 알림

```json
{
  "name": "trigger_navigation_notification",
  "description": "Show navigation warning notification",
  "arguments": {
    "message": "string",
    "level": {
      "type": "string",
      "enum": ["info", "warning", "critical"]
    }
  }
}
```

---

## Output Tool 3. 졸음 경고 사운드

```json
{
  "name": "trigger_drowsiness_alert_sound",
  "description": "Play drowsiness alert sound",
  "arguments": {
    "volume_percent": "number"
  }
}
```

---

## Output Tool 4. 계기판 시각 경고

```json
{
  "name": "trigger_cluster_visual_warning",
  "description": "Display visual warning on cluster",
  "arguments": {
    "icon": "string",
    "color": "string"
  }
}
```

---

## Output Tool 5. HUD 경고 메시지

```json
{
  "name": "trigger_hud_warning",
  "description": "Display HUD warning",
  "arguments": {
    "message": "string"
  }
}
```

---

## Output Tool 6. 운전자 주의 환기 음성

```json
{
  "name": "trigger_voice_prompt",
  "description": "Play voice prompt to driver",
  "arguments": {
    "text": "string",
    "priority": {
      "type": "string",
      "enum": ["normal", "high"]
    }
  }
}
```

---

## Output Tool 7. 경고 강도 단계 상승

```json
{
  "name": "escalate_warning_level",
  "description": "Escalate warning level",
  "arguments": {
    "current_level": "string",
    "target_level": "string"
  }
}
```

---

## Output Tool 8. 휴식 권장 알림

```json
{
  "name": "trigger_rest_recommendation",
  "description": "Recommend rest to driver",
  "arguments": {
    "reason": "string"
  }
}
```

---

## Output Tool 9. 로그 기록 (데모용 중요)

```json
{
  "name": "log_safety_event",
  "description": "Log safety-related event",
  "arguments": {
    "event_type": "string",
    "severity": "string"
  }
}
```

---

## Output Tool 10. 비상 모드 진입 요청 (확장용)

```json
{
  "name": "request_safe_mode",
  "description": "Request vehicle to enter safe mode",
  "arguments": {
    "reason": "string"
  }
}
```

---

# 3. 지금 시나리오를 이 구조로 표현하면

**입력**

* `get_lane_departure_status(departed=true, confidence=7
* `get_driver_drowsiness_status(drowsy=true, confidence=80)`
* `get_steering_grip_status(hands_on=false)`

**Function Gemma 출력 (병렬 호출)**

```json
[
  { "name": "trigger_steering_vibration", "arguments": { "intensity": "high" } },
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