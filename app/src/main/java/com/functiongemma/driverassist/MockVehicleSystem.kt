package com.functiongemma.driverassist

class MockVehicleSystem {
    fun apply(previous: MockVehicleState, actions: List<VehicleAction>): MockVehicleState {
        var warningLevel = previous.warningLevel

        val newEvents = previous.events.toMutableList()
        val now = System.currentTimeMillis()

        for (action in actions) {
            when (action.name) {
                "escalate_warning_level" -> {
                    val level = action.arguments["level"]?.toString()?.lowercase()
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
                    newEvents += VehicleUiEvent(
                        timestampMs = now,
                        message = "log:$msg",
                    )
                }

                else -> {
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
