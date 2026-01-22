package com.functiongemma.driverassist

class MockVehicleSystem {
    fun apply(previous: MockVehicleState, actions: List<VehicleAction>): MockVehicleState {
        AppLog.i("vehicle.apply actions=${actions.size} prev_warning=${previous.warningLevel}")
        var warningLevel = previous.warningLevel

        val newEvents = previous.events.toMutableList()
        val now = System.currentTimeMillis()

        for (action in actions) {
            when (action.name) {
                "escalate_warning_level" -> {
                    val level = action.arguments["level"]?.toString()?.lowercase()
                    AppLog.i("vehicle.action escalate_warning_level level=$level")
                    warningLevel = when (level) {
                        "critical" -> WarningLevel.CRITICAL
                        "warning" -> WarningLevel.WARNING
                        "normal" -> WarningLevel.NORMAL
                        else -> warningLevel
                    }
                    newEvents += VehicleUiEvent(
                        timestampMs = now,
                        message = "warning_level=$level",
                    )
                }

                "log_safety_event" -> {
                    val msg = action.arguments["message"]?.toString() ?: "log"
                    AppLog.i("vehicle.action log_safety_event message=$msg")
                    newEvents += VehicleUiEvent(
                        timestampMs = now,
                        message = "log:$msg",
                    )
                }

                else -> {
                    AppLog.i("vehicle.action trigger name=${action.name}")
                    newEvents += VehicleUiEvent(
                        timestampMs = now,
                        message = "trigger:${action.name}",
                    )
                }
            }
        }

        val trimmedEvents = newEvents.takeLast(100)

        return previous.copy(
            warningLevel = warningLevel,
            lastActions = actions,
            events = trimmedEvents,
        )
    }
}
