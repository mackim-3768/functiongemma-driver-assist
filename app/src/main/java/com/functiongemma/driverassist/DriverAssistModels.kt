package com.functiongemma.driverassist

enum class WarningLevel {
    NORMAL,
    WARNING,
    CRITICAL,
}

data class LaneDepartureStatus(
    val departed: Boolean,
    val confidence: Double,
)

data class DriverDrowsinessStatus(
    val drowsy: Boolean,
    val confidence: Double,
)

data class SteeringGripStatus(
    val handsOn: Boolean,
)

data class DriverAssistContext(
    val laneDeparture: LaneDepartureStatus,
    val drowsiness: DriverDrowsinessStatus,
    val steeringGrip: SteeringGripStatus,
    val speedKph: Int,
    val forwardCollisionRisk: Double,
    val drivingDurationMinutes: Int,
)

data class VehicleAction(
    val name: String,
    val arguments: Map<String, Any?> = emptyMap(),
)

data class VehicleUiEvent(
    val timestampMs: Long,
    val message: String,
)

data class MockVehicleState(
    val warningLevel: WarningLevel = WarningLevel.NORMAL,
    val lastActions: List<VehicleAction> = emptyList(),
    val events: List<VehicleUiEvent> = emptyList(),
)
