@file:OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)

package com.functiongemma.driverassist

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Slider
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlin.math.roundToInt

@Composable
fun DriverAssistApp(viewModel: DriverAssistViewModel = viewModel()) {
    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
            BoxWithConstraints(modifier = Modifier.fillMaxSize()) {
                val isPhone = maxWidth < 600.dp

                if (isPhone) {
                    DriverAssistPhoneLayout(viewModel = viewModel)
                } else {
                    DriverAssistWideLayout(viewModel = viewModel)
                }

            }
        }
    }
}

@Composable
private fun SelectorPanel(
    modifier: Modifier,
    useLlm: Boolean,
    llmModelPath: String,
    onUseLlmChanged: (Boolean) -> Unit,
    onLlmModelPathChanged: (String) -> Unit,
) {
    Card(modifier = modifier) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(text = "Function Selector", fontWeight = FontWeight.SemiBold)
                    Text(
                        text = if (useLlm) "LLM(java-llama.cpp)" else "Stub",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Switch(
                    checked = useLlm,
                    onCheckedChange = onUseLlmChanged,
                )
            }

            OutlinedTextField(
                value = llmModelPath,
                onValueChange = onLlmModelPathChanged,
                modifier = Modifier.fillMaxWidth(),
                enabled = useLlm,
                label = { Text("GGUF model path") },
                singleLine = true,
            )
        }
    }
}

@Composable
private fun InputToolsPanel(
    modifier: Modifier,
    context: DriverAssistContext,
    onLaneDepartureDepartedChange: (Boolean) -> Unit,
    onLaneDepartureConfidenceChange: (Double) -> Unit,
    onDrowsyChange: (Boolean) -> Unit,
    onDrowsinessConfidenceChange: (Double) -> Unit,
    onHandsOnChange: (Boolean) -> Unit,
    onSpeedKphChange: (Int) -> Unit,
    onForwardCollisionRiskChange: (Double) -> Unit,
    onDrivingDurationMinutesChange: (Int) -> Unit,
) {
    Card(modifier = modifier) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(text = "Input Tools", fontWeight = FontWeight.SemiBold)

            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(text = "get_lane_departure_status", style = MaterialTheme.typography.labelSmall)
                    Text(text = "departed", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = context.laneDeparture.departed,
                    onCheckedChange = onLaneDepartureDepartedChange,
                )
            }

            Text(
                text = "confidence: ${(context.laneDeparture.confidence * 100).roundToInt()}%",
                style = MaterialTheme.typography.bodySmall,
            )
            Slider(
                value = context.laneDeparture.confidence.toFloat(),
                onValueChange = { onLaneDepartureConfidenceChange(it.toDouble()) },
                valueRange = 0f..1f,
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(text = "get_driver_drowsiness_status", style = MaterialTheme.typography.labelSmall)
                    Text(text = "drowsy", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = context.drowsiness.drowsy,
                    onCheckedChange = onDrowsyChange,
                )
            }

            Text(
                text = "confidence: ${(context.drowsiness.confidence * 100).roundToInt()}%",
                style = MaterialTheme.typography.bodySmall,
            )
            Slider(
                value = context.drowsiness.confidence.toFloat(),
                onValueChange = { onDrowsinessConfidenceChange(it.toDouble()) },
                valueRange = 0f..1f,
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(text = "get_steering_grip_status", style = MaterialTheme.typography.labelSmall)
                    Text(text = "hands_on", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = context.steeringGrip.handsOn,
                    onCheckedChange = onHandsOnChange,
                )
            }

            Text(
                text = "get_vehicle_speed: ${context.speedKph} km/h",
                style = MaterialTheme.typography.bodySmall,
            )
            Slider(
                value = context.speedKph.toFloat(),
                onValueChange = { onSpeedKphChange(it.roundToInt()) },
                valueRange = 0f..240f,
            )

            Text(
                text = "get_forward_collision_risk: ${(context.forwardCollisionRisk * 100).roundToInt()}%",
                style = MaterialTheme.typography.bodySmall,
            )
            Slider(
                value = context.forwardCollisionRisk.toFloat(),
                onValueChange = { onForwardCollisionRiskChange(it.toDouble()) },
                valueRange = 0f..1f,
            )

            Text(
                text = "get_driving_duration_status: ${context.drivingDurationMinutes} min",
                style = MaterialTheme.typography.bodySmall,
            )
            Slider(
                value = context.drivingDurationMinutes.toFloat(),
                onValueChange = { onDrivingDurationMinutesChange(it.roundToInt()) },
                valueRange = 0f..240f,
            )
        }
    }
}

@Composable
private fun DriverAssistWideLayout(viewModel: DriverAssistViewModel) {
    Column(modifier = Modifier.fillMaxSize()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
        ) {
            ScenarioPanel(
                modifier = Modifier
                    .weight(0.28f)
                    .fillMaxSize(),
                scenarios = viewModel.scenarios,
                selectedTitle = viewModel.selectedScenarioTitle,
                onSelect = viewModel::selectScenario,
            )

            Spacer(modifier = Modifier.width(12.dp))

            MainPanel(
                modifier = Modifier
                    .weight(0.72f)
                    .fillMaxSize(),
                context = viewModel.context,
                vehicleState = viewModel.vehicleState,
                engineerJson = viewModel.engineerJson,
                engineerModeEnabled = viewModel.engineerModeEnabled,
                onEngineerModeChanged = viewModel::setEngineerMode,
                useLlm = viewModel.useLlm,
                llmModelPath = viewModel.llmModelPath,
                onUseLlmChanged = viewModel::setUseLlm,
                onLlmModelPathChanged = viewModel::setLlmModelPath,
                onLaneDepartureDepartedChange = viewModel::setLaneDepartureDeparted,
                onLaneDepartureConfidenceChange = viewModel::setLaneDepartureConfidence,
                onDrowsyChange = viewModel::setDrowsy,
                onDrowsinessConfidenceChange = viewModel::setDrowsinessConfidence,
                onHandsOnChange = viewModel::setHandsOn,
                onSpeedKphChange = viewModel::setSpeedKph,
                onForwardCollisionRiskChange = viewModel::setForwardCollisionRisk,
                onDrivingDurationMinutesChange = viewModel::setDrivingDurationMinutes,
            )
        }

        PromptBar(
            modifier = Modifier.fillMaxWidth(),
            prompt = viewModel.prompt,
            onPromptChange = viewModel::updatePrompt,
            onRun = viewModel::run,
        )
    }
}

@Composable
private fun DriverAssistPhoneLayout(viewModel: DriverAssistViewModel) {
    var showScenarioSheet by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    if (showScenarioSheet) {
        ModalBottomSheet(
            onDismissRequest = { showScenarioSheet = false },
            sheetState = sheetState,
        ) {
            ScenarioPanel(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp),
                scenarios = viewModel.scenarios,
                selectedTitle = viewModel.selectedScenarioTitle,
                onSelect = {
                    viewModel.selectScenario(it)
                    showScenarioSheet = false
                },
            )
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(text = "Scenario", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(text = viewModel.selectedScenarioTitle, fontWeight = FontWeight.SemiBold)
                }
                Spacer(modifier = Modifier.width(12.dp))
                Button(onClick = { showScenarioSheet = true }) {
                    Text("Select")
                }
            }
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
        ) {
            MainPanelCompact(
                modifier = Modifier.fillMaxSize(),
                context = viewModel.context,
                vehicleState = viewModel.vehicleState,
                engineerJson = viewModel.engineerJson,
                engineerModeEnabled = viewModel.engineerModeEnabled,
                onEngineerModeChanged = viewModel::setEngineerMode,
                useLlm = viewModel.useLlm,
                llmModelPath = viewModel.llmModelPath,
                onUseLlmChanged = viewModel::setUseLlm,
                onLlmModelPathChanged = viewModel::setLlmModelPath,
                onLaneDepartureDepartedChange = viewModel::setLaneDepartureDeparted,
                onLaneDepartureConfidenceChange = viewModel::setLaneDepartureConfidence,
                onDrowsyChange = viewModel::setDrowsy,
                onDrowsinessConfidenceChange = viewModel::setDrowsinessConfidence,
                onHandsOnChange = viewModel::setHandsOn,
                onSpeedKphChange = viewModel::setSpeedKph,
                onForwardCollisionRiskChange = viewModel::setForwardCollisionRisk,
                onDrivingDurationMinutesChange = viewModel::setDrivingDurationMinutes,
            )
        }

        PromptBar(
            modifier = Modifier.fillMaxWidth(),
            prompt = viewModel.prompt,
            onPromptChange = viewModel::updatePrompt,
            onRun = viewModel::run,
        )
    }
}

@Composable
private fun ScenarioPanel(
    modifier: Modifier,
    scenarios: List<Scenario>,
    selectedTitle: String,
    onSelect: (Scenario) -> Unit,
) {
    Card(modifier = modifier) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(text = "Scenario", fontWeight = FontWeight.SemiBold)
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                for (scenario in scenarios) {
                    val isSelected = scenario.title == selectedTitle
                    Button(
                        onClick = { onSelect(scenario) },
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(
                            text = if (isSelected) "✓ ${scenario.title}" else scenario.title,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
            }

            Text(
                text = "Tip: 버튼을 누르면 Prompt/Context가 자동 반영됩니다.",
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

@Composable
private fun MainPanel(
    modifier: Modifier,
    context: DriverAssistContext,
    vehicleState: MockVehicleState,
    engineerJson: String,
    engineerModeEnabled: Boolean,
    onEngineerModeChanged: (Boolean) -> Unit,
    useLlm: Boolean,
    llmModelPath: String,
    onUseLlmChanged: (Boolean) -> Unit,
    onLlmModelPathChanged: (String) -> Unit,
    onLaneDepartureDepartedChange: (Boolean) -> Unit,
    onLaneDepartureConfidenceChange: (Double) -> Unit,
    onDrowsyChange: (Boolean) -> Unit,
    onDrowsinessConfidenceChange: (Double) -> Unit,
    onHandsOnChange: (Boolean) -> Unit,
    onSpeedKphChange: (Int) -> Unit,
    onForwardCollisionRiskChange: (Double) -> Unit,
    onDrivingDurationMinutesChange: (Int) -> Unit,
) {
    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        HudPanel(
            modifier = Modifier.fillMaxWidth(),
            context = context,
            warningLevel = vehicleState.warningLevel,
        )

        InputToolsPanel(
            modifier = Modifier.fillMaxWidth(),
            context = context,
            onLaneDepartureDepartedChange = onLaneDepartureDepartedChange,
            onLaneDepartureConfidenceChange = onLaneDepartureConfidenceChange,
            onDrowsyChange = onDrowsyChange,
            onDrowsinessConfidenceChange = onDrowsinessConfidenceChange,
            onHandsOnChange = onHandsOnChange,
            onSpeedKphChange = onSpeedKphChange,
            onForwardCollisionRiskChange = onForwardCollisionRiskChange,
            onDrivingDurationMinutesChange = onDrivingDurationMinutesChange,
        )

        SelectorPanel(
            modifier = Modifier.fillMaxWidth(),
            useLlm = useLlm,
            llmModelPath = llmModelPath,
            onUseLlmChanged = onUseLlmChanged,
            onLlmModelPathChanged = onLlmModelPathChanged,
        )

        Card(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(text = "Engineer Mode", fontWeight = FontWeight.SemiBold)
                Switch(
                    checked = engineerModeEnabled,
                    onCheckedChange = onEngineerModeChanged,
                )
            }
        }

        if (engineerModeEnabled) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(0.55f),
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(text = "Function Call JSON", fontWeight = FontWeight.SemiBold)
                    Text(
                        text = engineerJson,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState()),
                    )
                }
            }
        }

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .weight(0.45f),
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(text = "Mock Vehicle Log", fontWeight = FontWeight.SemiBold)
                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    items(vehicleState.events.reversed()) { ev ->
                        Text(text = "${ev.timestampMs}: ${ev.message}", style = MaterialTheme.typography.bodySmall)
                        Spacer(modifier = Modifier.height(6.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun MainPanelCompact(
    modifier: Modifier,
    context: DriverAssistContext,
    vehicleState: MockVehicleState,
    engineerJson: String,
    engineerModeEnabled: Boolean,
    onEngineerModeChanged: (Boolean) -> Unit,
    useLlm: Boolean,
    llmModelPath: String,
    onUseLlmChanged: (Boolean) -> Unit,
    onLlmModelPathChanged: (String) -> Unit,
    onLaneDepartureDepartedChange: (Boolean) -> Unit,
    onLaneDepartureConfidenceChange: (Double) -> Unit,
    onDrowsyChange: (Boolean) -> Unit,
    onDrowsinessConfidenceChange: (Double) -> Unit,
    onHandsOnChange: (Boolean) -> Unit,
    onSpeedKphChange: (Int) -> Unit,
    onForwardCollisionRiskChange: (Double) -> Unit,
    onDrivingDurationMinutesChange: (Int) -> Unit,
) {
    LazyColumn(
        modifier = modifier,
        contentPadding = PaddingValues(12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            HudPanel(
                modifier = Modifier.fillMaxWidth(),
                context = context,
                warningLevel = vehicleState.warningLevel,
            )
        }

        item {
            InputToolsPanel(
                modifier = Modifier.fillMaxWidth(),
                context = context,
                onLaneDepartureDepartedChange = onLaneDepartureDepartedChange,
                onLaneDepartureConfidenceChange = onLaneDepartureConfidenceChange,
                onDrowsyChange = onDrowsyChange,
                onDrowsinessConfidenceChange = onDrowsinessConfidenceChange,
                onHandsOnChange = onHandsOnChange,
                onSpeedKphChange = onSpeedKphChange,
                onForwardCollisionRiskChange = onForwardCollisionRiskChange,
                onDrivingDurationMinutesChange = onDrivingDurationMinutesChange,
            )
        }

        item {
            SelectorPanel(
                modifier = Modifier.fillMaxWidth(),
                useLlm = useLlm,
                llmModelPath = llmModelPath,
                onUseLlmChanged = onUseLlmChanged,
                onLlmModelPathChanged = onLlmModelPathChanged,
            )
        }

        item {
            Card(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Text(text = "Engineer Mode", fontWeight = FontWeight.SemiBold)
                    Switch(
                        checked = engineerModeEnabled,
                        onCheckedChange = onEngineerModeChanged,
                    )
                }
            }
        }

        if (engineerModeEnabled) {
            item {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(text = "Function Call JSON", fontWeight = FontWeight.SemiBold)
                        Text(
                            text = engineerJson,
                            style = MaterialTheme.typography.bodySmall,
                            modifier = Modifier
                                .fillMaxWidth()
                                .heightIn(max = 240.dp)
                                .verticalScroll(rememberScrollState()),
                        )
                    }
                }
            }
        }

        item {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(text = "Mock Vehicle Log", fontWeight = FontWeight.SemiBold)
                    val recent = vehicleState.events.takeLast(30).asReversed()
                    for (ev in recent) {
                        Text(
                            text = "${ev.timestampMs}: ${ev.message}",
                            style = MaterialTheme.typography.bodySmall,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun HudPanel(
    modifier: Modifier,
    context: DriverAssistContext,
    warningLevel: WarningLevel,
) {
    val levelColor = when (warningLevel) {
        WarningLevel.NORMAL -> MaterialTheme.colorScheme.primary
        WarningLevel.WARNING -> Color(0xFFFFA000)
        WarningLevel.CRITICAL -> MaterialTheme.colorScheme.error
    }

    Card(modifier = modifier) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(text = "Passenger View / HUD", fontWeight = FontWeight.SemiBold)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .width(10.dp)
                            .height(10.dp)
                            .background(levelColor),
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(text = warningLevel.name)
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                HudValue(label = "Speed", value = "${context.speedKph} km/h")
                HudValue(label = "Lane", value = if (context.laneDeparture.departed) "DEPARTED" else "OK")
                HudValue(label = "Drowsy", value = if (context.drowsiness.drowsy) "YES" else "NO")
                HudValue(label = "Hands", value = if (context.steeringGrip.handsOn) "ON" else "OFF")
            }

            Text(
                text = "Front view (placeholder)",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun HudValue(label: String, value: String) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(text = label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(text = value, fontWeight = FontWeight.Medium)
    }
}

@Composable
private fun PromptBar(
    modifier: Modifier,
    prompt: String,
    onPromptChange: (String) -> Unit,
    onRun: () -> Unit,
) {
    Card(modifier = modifier) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            OutlinedTextField(
                value = prompt,
                onValueChange = onPromptChange,
                modifier = Modifier.weight(1f),
                label = { Text("Prompt") },
                singleLine = true,
            )
            Button(onClick = onRun) {
                Text("Run")
            }
        }
    }
}
