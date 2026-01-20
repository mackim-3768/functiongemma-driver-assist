package com.functiongemma.driverassist

enum class ScenarioEvent {
    NONE,
    LANE_DEPARTURE_HIGH_SPEED,
    DROWSY_CONFIDENT,
    DROWSY_NO_HANDS,
    FORWARD_COLLISION_HIGH,
    MANUAL_TRIGGER
}

data class GateResult(
    val triggered: Boolean,
    val event: ScenarioEvent,
    val reason: String
)

class ScenarioGate {
    fun evaluate(context: DriverAssistContext): GateResult {
        // DROWSY_NO_HANDS: drowsy == true && confidence >= 0.8 && hands_on == false
        if (context.drowsiness.drowsy && context.drowsiness.confidence >= 0.8 && !context.steeringGrip.handsOn) {
            return GateResult(true, ScenarioEvent.DROWSY_NO_HANDS, "Drowsy(>=0.8) + No Hands")
        }

        // DROWSY_CONFIDENT: drowsy == true && confidence >= 0.9 (Simple High confidence)
        if (context.drowsiness.drowsy && context.drowsiness.confidence >= 0.9) {
             return GateResult(true, ScenarioEvent.DROWSY_CONFIDENT, "Drowsy(>=0.9)")
        }

        // LANE_DEPARTURE_HIGH_SPEED: departed == true && confidence >= 0.7 && speed_kph >= 60
        if (context.laneDeparture.departed && context.laneDeparture.confidence >= 0.7 && context.speedKph >= 60) {
            return GateResult(true, ScenarioEvent.LANE_DEPARTURE_HIGH_SPEED, "Lane Departure(>=0.7) + Speed(${context.speedKph}kph)")
        }

        // FORWARD_COLLISION_HIGH: risk >= 0.75
        if (context.forwardCollisionRisk >= 0.75) {
            return GateResult(true, ScenarioEvent.FORWARD_COLLISION_HIGH, "Forward Collision Risk(${context.forwardCollisionRisk})")
        }

        return GateResult(false, ScenarioEvent.NONE, "No significant risk detected")
    }
}

data class SafetyResult(
    val executedActions: List<VehicleAction>,
    val blockedActions: List<VehicleAction>,
    val logs: List<String>
)

class SafetyGate {
    private val cooldownMap = mutableMapOf<String, Long>()
    private val COOLDOWN_MS = 5000L // 5 seconds

    fun filter(actions: List<VehicleAction>): SafetyResult {
        val executed = mutableListOf<VehicleAction>()
        val blocked = mutableListOf<VehicleAction>()
        val logs = mutableListOf<String>()
        val now = System.currentTimeMillis()

        for (action in actions) {
            // Bypass logging actions from cooldown
            if (action.name == "log_safety_event") {
                executed.add(action)
                continue
            }

            // Cooldown check
            if (isCooldownApplicable(action.name)) {
                val lastRun = cooldownMap[action.name] ?: 0L
                if (now - lastRun < COOLDOWN_MS) {
                    blocked.add(action)
                    logs.add("SafetyGate: Blocked ${action.name} (Cooldown ${(COOLDOWN_MS - (now - lastRun))/1000}s)")
                    continue
                }
            }

            // Parameter Safety (Example: Volume/Intensity Check)
            // For now, we just pass through, but we could clamp values here.

            executed.add(action)
            cooldownMap[action.name] = now
        }

        return SafetyResult(executed, blocked, logs)
    }

    private fun isCooldownApplicable(actionName: String): Boolean {
        // Log events are always allowed
        if (actionName == "log_safety_event" || actionName == "request_safe_mode") return false
        
        // Alerts should have cooldown
        return true
    }
    
    fun clear() {
        cooldownMap.clear()
    }
}
