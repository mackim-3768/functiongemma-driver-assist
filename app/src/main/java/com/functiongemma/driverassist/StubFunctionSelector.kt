package com.functiongemma.driverassist

interface FunctionSelector {
    fun select(context: DriverAssistContext, prompt: String): List<VehicleAction>
}

class StubFunctionSelector : FunctionSelector {
    override fun select(context: DriverAssistContext, prompt: String): List<VehicleAction> {
        val actions = mutableListOf<VehicleAction>()

        val laneTriggered = context.laneDeparture.departed || prompt.contains("차선")
        val drowsyTriggered = context.drowsiness.drowsy || prompt.contains("졸")
        val collisionTriggered = context.forwardCollisionRisk >= 0.7 || prompt.contains("충돌")

        if (laneTriggered) {
            actions += VehicleAction(
                name = "trigger_steering_vibration",
                arguments = mapOf("intensity" to "high"),
            )
            actions += VehicleAction(
                name = "trigger_hud_warning",
                arguments = mapOf("message" to "차선 이탈 감지", "level" to "warning"),
            )
        }

        if (drowsyTriggered) {
            actions += VehicleAction(
                name = "trigger_drowsiness_alert_sound",
                arguments = mapOf("volume_percent" to 100),
            )
            actions += VehicleAction(
                name = "trigger_voice_prompt",
                arguments = mapOf("message" to "졸고 계신가요?", "level" to "critical"),
            )
            actions += VehicleAction(
                name = "escalate_warning_level",
                arguments = mapOf("level" to "critical"),
            )
        }

        if (!context.steeringGrip.handsOn || prompt.contains("핸들") || prompt.contains("미그립")) {
            actions += VehicleAction(
                name = "trigger_cluster_visual_warning",
                arguments = mapOf("message" to "핸들 그립 확인", "level" to "warning"),
            )
        }

        if (collisionTriggered) {
            actions += VehicleAction(
                name = "trigger_cluster_visual_warning",
                arguments = mapOf("message" to "전방 충돌 위험", "level" to "critical"),
            )
            actions += VehicleAction(
                name = "trigger_hud_warning",
                arguments = mapOf("message" to "전방 주의", "level" to "critical"),
            )
            actions += VehicleAction(
                name = "escalate_warning_level",
                arguments = mapOf("level" to "critical"),
            )
        }

        if (actions.isEmpty()) {
            actions += VehicleAction(
                name = "log_safety_event",
                arguments = mapOf("message" to "no_action_selected"),
            )
        } else {
            actions += VehicleAction(
                name = "log_safety_event",
                arguments = mapOf(
                    "message" to "actions_selected",
                    "count" to actions.size,
                ),
            )
        }

        return actions
    }
}
