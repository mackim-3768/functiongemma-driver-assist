package com.functiongemma.driverassist

import org.json.JSONArray
import org.json.JSONObject
import java.io.File

class LlamaCppFunctionSelector(
    private val modelPath: String,
    private val temperature: Float = 0.2f,
) : FunctionSelector, AutoCloseable {

    private var model: Any? = null

    override fun select(context: DriverAssistContext, prompt: String): List<VehicleAction> {
        if (modelPath.isBlank()) {
            AppLog.w("llm.select model_path_blank")
            return listOf(
                VehicleAction(
                    name = "log_safety_event",
                    arguments = mapOf("message" to "llama_cpp_model_path_blank"),
                ),
            )
        }

        val modelFile = runCatching { File(modelPath) }.getOrNull()
        if (modelFile == null || !modelFile.exists() || modelFile.length() <= 0L || !modelFile.canRead()) {
            AppLog.w(
                "llm.select model_not_readable path=$modelPath " +
                    "exists=${modelFile?.exists() == true} can_read=${modelFile?.canRead() == true} bytes=${modelFile?.length() ?: -1L}"
            )
            return listOf(
                VehicleAction(
                    name = "log_safety_event",
                    arguments = mapOf(
                        "message" to "llama_cpp_model_not_readable",
                        "path" to modelPath,
                        "exists" to (modelFile?.exists() == true),
                        "can_read" to (modelFile?.canRead() == true),
                        "bytes" to (modelFile?.length() ?: -1L),
                    ),
                ),
            )
        }

        return try {
            AppLog.i("llm.select start path=$modelPath bytes=${modelFile.length()} prompt_chars=${prompt.length} temp=$temperature")
            val llamaModel = ensureModel()
            val input = buildPrompt(context = context, userPrompt = prompt)
            val outputText = complete(llamaModel, input)
            val jsonText = extractJsonArrayText(outputText)
            AppLog.i("llm.select output_chars=${outputText.length} json_chars=${jsonText.length}")
            parseActions(jsonText)
        } catch (t: Throwable) {
            AppLog.e("llm.select error path=$modelPath", t)
            val msg = (t.message ?: t::class.java.simpleName).take(200)
            listOf(
                VehicleAction(
                    name = "log_safety_event",
                    arguments = mapOf(
                        "message" to "llama_cpp_error",
                        "error_type" to t::class.java.name,
                        "detail" to msg,
                    ),
                ),
            )
        }
    }

    override fun close() {
        val current = model ?: return
        AppLog.i("llm.close")
        runCatching {
            current.javaClass.getMethod("close").invoke(current)
        }
        model = null
    }

    private fun ensureModel(): Any {
        val existing = model
        if (existing != null) return existing

        AppLog.i("llm.ensure_model start")

        val modelParamsClass = Class.forName("de.kherud.llama.ModelParameters")
        val llamaModelClass = Class.forName("de.kherud.llama.LlamaModel")

        val modelParams = modelParamsClass.getConstructor().newInstance()
        modelParamsClass.getMethod("setModel", String::class.java).invoke(modelParams, modelPath)

        val newModel = llamaModelClass.getConstructor(modelParamsClass).newInstance(modelParams)
        model = newModel
        AppLog.i("llm.ensure_model done")
        return newModel
    }

    private fun complete(llamaModel: Any, prompt: String): String {
        val inferParamsClass = Class.forName("de.kherud.llama.InferenceParameters")
        val inferParams = inferParamsClass.getConstructor(String::class.java).newInstance(prompt)

        runCatching {
            inferParamsClass.getMethod("setTemperature", Float::class.javaPrimitiveType).invoke(inferParams, temperature)
        }

        val result = llamaModel.javaClass.getMethod("complete", inferParamsClass).invoke(llamaModel, inferParams)
        return result?.toString().orEmpty()
    }

    private fun buildPrompt(context: DriverAssistContext, userPrompt: String): String {
        val ctx = JSONObject()
        ctx.put("lane_departure", JSONObject().put("departed", context.laneDeparture.departed).put("confidence", context.laneDeparture.confidence))
        ctx.put("driver_drowsiness", JSONObject().put("drowsy", context.drowsiness.drowsy).put("confidence", context.drowsiness.confidence))
        ctx.put("steering_grip", JSONObject().put("hands_on", context.steeringGrip.handsOn))
        ctx.put("vehicle_speed_kph", context.speedKph)
        ctx.put("forward_collision_risk", context.forwardCollisionRisk)
        ctx.put("driving_duration_minutes", context.drivingDurationMinutes)

        return """
You are FunctionGemma, a function selection model for a driver assistance demo.

Input context is structured sensor state (do not invent fields):
${ctx.toString(2)}

User prompt:
$userPrompt

Return ONLY a JSON array of tool calls. Each item must be:
{"name": "<tool_name>", "arguments": { ... }}

Allowed tool names:
- trigger_steering_vibration
- trigger_navigation_notification
- trigger_drowsiness_alert_sound
- trigger_cluster_visual_warning
- trigger_hud_warning
- trigger_voice_prompt
- escalate_warning_level
- trigger_rest_recommendation
- log_safety_event
- request_safe_mode

If no action is needed, return:
[{"name":"log_safety_event","arguments":{"message":"no_action_selected"}}]
""".trim()
    }

    private fun extractJsonArrayText(text: String): String {
        val start = text.indexOf('[')
        val end = text.lastIndexOf(']')
        if (start == -1 || end == -1 || end <= start) {
            throw IllegalStateException("No JSON array found in model output")
        }
        return text.substring(start, end + 1)
    }

    private fun parseActions(jsonArrayText: String): List<VehicleAction> {
        val array = JSONArray(jsonArrayText)
        val actions = ArrayList<VehicleAction>(array.length())

        for (i in 0 until array.length()) {
            val obj = array.optJSONObject(i) ?: continue
            val name = obj.optString("name").orEmpty()
            if (name.isBlank()) continue

            val argsObj = obj.optJSONObject("arguments") ?: JSONObject()
            val args = mutableMapOf<String, Any?>()
            val keys = argsObj.keys()
            while (keys.hasNext()) {
                val k = keys.next()
                args[k] = argsObj.opt(k)
            }

            actions += VehicleAction(name = name, arguments = args)
        }

        return actions
    }
}
