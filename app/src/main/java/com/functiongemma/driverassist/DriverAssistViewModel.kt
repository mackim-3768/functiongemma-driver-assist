package com.functiongemma.driverassist

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import org.json.JSONArray
import org.json.JSONObject

class DriverAssistViewModel(
    private val selector: FunctionSelector = StubFunctionSelector(),
    private val mockVehicleSystem: MockVehicleSystem = MockVehicleSystem(),
) : ViewModel() {

    val scenarios: List<Scenario> = listOf(
        Scenario(
            title = "차선 이탈",
            prompt = "차선 이탈이 감지됐고 운전자가 핸들을 잡지 않았어",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = true, confidence = 0.7),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.2),
                steeringGrip = SteeringGripStatus(handsOn = false),
                speedKph = 80,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 20,
            ),
        ),
        Scenario(
            title = "졸음",
            prompt = "졸음 운전이 의심돼",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.1),
                drowsiness = DriverDrowsinessStatus(drowsy = true, confidence = 0.8),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 70,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 90,
            ),
        ),
        Scenario(
            title = "핸들 미그립",
            prompt = "운전자가 핸들을 잡지 않았어",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.1),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.2),
                steeringGrip = SteeringGripStatus(handsOn = false),
                speedKph = 60,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 30,
            ),
        ),
        Scenario(
            title = "전방 충돌",
            prompt = "전방 충돌 위험이 높아",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.1),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.2),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 90,
                forwardCollisionRisk = 0.9,
                drivingDurationMinutes = 15,
            ),
        ),
    )

    var selectedScenarioTitle by mutableStateOf(scenarios.first().title)
        private set

    var context by mutableStateOf(scenarios.first().context)
        private set

    var prompt by mutableStateOf(scenarios.first().prompt)
        private set

    var engineerModeEnabled by mutableStateOf(true)
        private set

    var engineerJson by mutableStateOf("[]")
        private set

    var vehicleState by mutableStateOf(MockVehicleState())
        private set

    fun selectScenario(scenario: Scenario) {
        selectedScenarioTitle = scenario.title
        context = scenario.context
        prompt = scenario.prompt
    }

    fun updatePrompt(value: String) {
        prompt = value
    }

    fun setEngineerModeEnabled(enabled: Boolean) {
        engineerModeEnabled = enabled
    }

    fun run() {
        val actions = selector.select(context = context, prompt = prompt)
        engineerJson = actionsToJson(actions)
        vehicleState = mockVehicleSystem.apply(vehicleState, actions)
    }

    private fun actionsToJson(actions: List<VehicleAction>): String {
        val array = JSONArray()
        for (action in actions) {
            val obj = JSONObject()
            obj.put("name", action.name)
            val args = JSONObject()
            for ((k, v) in action.arguments) {
                args.put(k, v)
            }
            obj.put("arguments", args)
            array.put(obj)
        }
        return array.toString(2)
    }
}

data class Scenario(
    val title: String,
    val prompt: String,
    val context: DriverAssistContext,
)
