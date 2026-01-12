package com.functiongemma.driverassist

import android.app.Application
import android.os.SystemClock
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

class DriverAssistViewModel(
    application: Application,
    private val selector: FunctionSelector,
    private val mockVehicleSystem: MockVehicleSystem,
) : AndroidViewModel(application) {

    constructor(application: Application) : this(
        application = application,
        selector = StubFunctionSelector(),
        mockVehicleSystem = MockVehicleSystem(),
    )

    enum class ModelDownloadPhase {
        Idle,
        Checking,
        Downloading,
        Ready,
        Error,
    }

    data class ModelDownloadState(
        val phase: ModelDownloadPhase = ModelDownloadPhase.Idle,
        val resolvedModelPath: String = "",
        val bytesDownloaded: Long = 0L,
        val bytesTotal: Long = 0L,
        val message: String = "",
    ) {
        val progressFraction: Float?
            get() = if (phase == ModelDownloadPhase.Downloading && bytesTotal > 0L) {
                bytesDownloaded.toFloat() / bytesTotal.toFloat()
            } else {
                null
            }
    }

    private val appConfig: AppConfig? = runCatching {
        AppConfigLoader.load(getApplication())
    }.getOrNull()

    private var modelDownloadJob: Job? = null

    var modelDownloadState by mutableStateOf(ModelDownloadState())
        private set

    val scenarios: List<Scenario> = listOf(
        Scenario(
            title = "정상 주행",
            prompt = "상태 확인",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.1),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.1),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 80,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 10,
            ),
        ),
        Scenario(
            title = "차선 이탈(센서)",
            prompt = "차선 이탈이 감지됐어",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = true, confidence = 0.7),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.2),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 85,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 20,
            ),
        ),
        Scenario(
            title = "차선 이탈 + 핸들 미그립",
            prompt = "차선 이탈이 감지됐고 운전자가 핸들을 잡지 않았어",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = true, confidence = 0.8),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.2),
                steeringGrip = SteeringGripStatus(handsOn = false),
                speedKph = 90,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 25,
            ),
        ),
        Scenario(
            title = "차선 이탈(프롬프트)",
            prompt = "차선이 흔들리는 것 같아",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.2),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.2),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 70,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 15,
            ),
        ),
        Scenario(
            title = "졸음(센서)",
            prompt = "졸음 운전이 의심돼",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.1),
                drowsiness = DriverDrowsinessStatus(drowsy = true, confidence = 0.85),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 70,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 90,
            ),
        ),
        Scenario(
            title = "졸음(프롬프트)",
            prompt = "졸 것 같아. 경고해줘",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.1),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.3),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 75,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 80,
            ),
        ),
        Scenario(
            title = "핸들 미그립(센서)",
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
            title = "핸들 미그립(프롬프트)",
            prompt = "핸들 미그립 같아",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.1),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.2),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 55,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 25,
            ),
        ),
        Scenario(
            title = "전방 충돌 위험(센서)",
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
        Scenario(
            title = "전방 충돌 위험(프롬프트)",
            prompt = "충돌 위험 같은데?",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.1),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.2),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 50,
                forwardCollisionRisk = 0.2,
                drivingDurationMinutes = 15,
            ),
        ),
        Scenario(
            title = "복합 위험(차선+졸음+충돌)",
            prompt = "차선도 흔들리고 졸리고 전방 충돌 위험도 있어",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = true, confidence = 0.9),
                drowsiness = DriverDrowsinessStatus(drowsy = true, confidence = 0.9),
                steeringGrip = SteeringGripStatus(handsOn = false),
                speedKph = 100,
                forwardCollisionRisk = 0.95,
                drivingDurationMinutes = 120,
            ),
        ),
        Scenario(
            title = "경계 상태(노이즈)",
            prompt = "라인이 조금 흔들리는 느낌",
            context = DriverAssistContext(
                laneDeparture = LaneDepartureStatus(departed = false, confidence = 0.55),
                drowsiness = DriverDrowsinessStatus(drowsy = false, confidence = 0.4),
                steeringGrip = SteeringGripStatus(handsOn = true),
                speedKph = 65,
                forwardCollisionRisk = 0.6,
                drivingDurationMinutes = 40,
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

    var useLlm by mutableStateOf(false)
        private set

    var llmModelPath by mutableStateOf("")
        private set

    private var llamaSelector: LlamaCppFunctionSelector? = null

    init {
        val config = appConfig
        if (config != null) {
            if (llmModelPath.isBlank() && config.preferredModelPath.isNotBlank()) {
                llmModelPath = config.preferredModelPath
            }
            if (config.autoDownloadOnStart) {
                ensureModelReady(forceDownload = false)
            }
        } else {
            modelDownloadState = ModelDownloadState(
                phase = ModelDownloadPhase.Error,
                message = "config_load_failed",
            )
        }
    }

    var vehicleState by mutableStateOf(MockVehicleState())
        private set

    private fun updateContext(update: (DriverAssistContext) -> DriverAssistContext) {
        context = update(context)
    }

    fun setLaneDepartureDeparted(departed: Boolean) {
        updateContext { it.copy(laneDeparture = it.laneDeparture.copy(departed = departed)) }
    }

    fun setLaneDepartureConfidence(confidence: Double) {
        updateContext { it.copy(laneDeparture = it.laneDeparture.copy(confidence = confidence.coerceIn(0.0, 1.0))) }
    }

    fun setDrowsy(drowsy: Boolean) {
        updateContext { it.copy(drowsiness = it.drowsiness.copy(drowsy = drowsy)) }
    }

    fun setDrowsinessConfidence(confidence: Double) {
        updateContext { it.copy(drowsiness = it.drowsiness.copy(confidence = confidence.coerceIn(0.0, 1.0))) }
    }

    fun setHandsOn(handsOn: Boolean) {
        updateContext { it.copy(steeringGrip = it.steeringGrip.copy(handsOn = handsOn)) }
    }

    fun setSpeedKph(speedKph: Int) {
        updateContext { it.copy(speedKph = speedKph.coerceIn(0, 240)) }
    }

    fun setForwardCollisionRisk(risk: Double) {
        updateContext { it.copy(forwardCollisionRisk = risk.coerceIn(0.0, 1.0)) }
    }

    fun setDrivingDurationMinutes(minutes: Int) {
        updateContext { it.copy(drivingDurationMinutes = minutes.coerceIn(0, 600)) }
    }

    fun selectScenario(scenario: Scenario) {
        selectedScenarioTitle = scenario.title
        context = scenario.context
        prompt = scenario.prompt
    }

    fun updatePrompt(value: String) {
        prompt = value
    }

    fun setEngineerMode(enabled: Boolean) {
        engineerModeEnabled = enabled
    }

    fun setUseLlm(enabled: Boolean) {
        useLlm = enabled
        if (!enabled) {
            closeLlm()
        } else {
            ensureModelReady(forceDownload = false)
        }
    }

    fun setLlmModelPath(path: String) {
        if (path == llmModelPath) return
        llmModelPath = path
        closeLlm()
    }

    private fun closeLlm() {
        llamaSelector?.close()
        llamaSelector = null
    }

    fun run() {
        val selectorToUse = if (useLlm) {
            llamaSelector ?: LlamaCppFunctionSelector(modelPath = llmModelPath).also { llamaSelector = it }
        } else {
            selector
        }

        val actions = selectorToUse.select(context = context, prompt = prompt)
        engineerJson = actionsToJson(actions)
        vehicleState = mockVehicleSystem.apply(vehicleState, actions)
    }

    override fun onCleared() {
        closeLlm()
        super.onCleared()
    }

    fun downloadModelNow() {
        ensureModelReady(forceDownload = true)
    }

    private fun ensureModelReady(forceDownload: Boolean) {
        val config = appConfig ?: run {
            modelDownloadState = ModelDownloadState(
                phase = ModelDownloadPhase.Error,
                message = "config_load_failed",
            )
            return
        }

        if (modelDownloadJob?.isActive == true) return

        modelDownloadJob = viewModelScope.launch {
            modelDownloadState = modelDownloadState.copy(
                phase = ModelDownloadPhase.Checking,
                message = "",
            )

            val preferred = runCatching { File(config.preferredModelPath) }.getOrNull()
            val fallback = resolveFallbackFile(config)

            val preferredOk = preferred != null && preferred.exists() && preferred.length() > 0L
            val fallbackOk = fallback.exists() && fallback.length() > 0L

            if (!forceDownload) {
                if (preferredOk) {
                    setModelReady(preferred!!.absolutePath)
                    return@launch
                }
                if (fallbackOk) {
                    setModelReady(fallback.absolutePath)
                    return@launch
                }
            }

            if (config.modelUrl.isBlank()) {
                modelDownloadState = ModelDownloadState(
                    phase = ModelDownloadPhase.Error,
                    message = "model_url_blank",
                )
                return@launch
            }

            val candidates = buildList {
                if (preferred != null && preferred.path.isNotBlank()) add(preferred)
                if (fallback.path.isNotBlank()) add(fallback)
            }.distinctBy { it.absolutePath }

            var lastError: Throwable? = null
            for (dest in candidates) {
                try {
                    var lastProgressUpdateMs = 0L

                    withContext(Dispatchers.IO) {
                        ModelDownloader.downloadToFile(
                            url = config.modelUrl,
                            hfToken = config.hfToken,
                            destFile = dest,
                        ) { p ->
                            val now = SystemClock.elapsedRealtime()
                            if (now - lastProgressUpdateMs >= 250L) {
                                lastProgressUpdateMs = now
                                viewModelScope.launch {
                                    modelDownloadState = ModelDownloadState(
                                        phase = ModelDownloadPhase.Downloading,
                                        resolvedModelPath = dest.absolutePath,
                                        bytesDownloaded = p.bytesDownloaded,
                                        bytesTotal = p.bytesTotal,
                                        message = "downloading",
                                    )
                                }
                            }
                        }
                    }

                    setModelReady(dest.absolutePath)
                    return@launch
                } catch (t: Throwable) {
                    lastError = t
                }
            }

            val msg = (lastError?.message ?: lastError?.javaClass?.simpleName ?: "download_failed").take(200)
            modelDownloadState = ModelDownloadState(
                phase = ModelDownloadPhase.Error,
                message = msg,
            )
        }
    }

    private fun resolveFallbackFile(config: AppConfig): File {
        val app = getApplication<Application>()
        val base = app.getExternalFilesDir(null) ?: app.filesDir
        return File(base, config.fallbackRelativePath)
    }

    private fun setModelReady(path: String) {
        modelDownloadState = ModelDownloadState(
            phase = ModelDownloadPhase.Ready,
            resolvedModelPath = path,
            message = "ready",
        )
        setLlmModelPath(path)
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
