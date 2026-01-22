package com.functiongemma.driverassist

import android.content.Context
import java.io.File

data class AppConfig(
    val modelUrl: String,
    val hfToken: String,
    val preferredModelPath: String,
    val fallbackRelativePath: String,
    val autoDownloadOnStart: Boolean,
)

object AppConfigLoader {
    fun load(context: Context, assetName: String = "application.yaml"): AppConfig {
        AppLog.i("config.load start assetName=$assetName")
        val text = readConfigText(context = context, assetName = assetName)
        val map = parseSimpleYaml(text)

        val modelUrl = map["model_url"].orEmpty()
        val hfToken = map["hf_token"].orEmpty()
        val preferredModelPath = map["preferred_model_path"].orEmpty()
        val fallbackRelativePath = map["fallback_relative_path"].orEmpty()
        val autoDownloadOnStart = map["auto_download_on_start"]?.toBooleanStrictOrNull() ?: false

        AppLog.i(
            "config.load done " +
                "model_url=${AppLog.summarizeUrl(modelUrl)} " +
                "hf_token=${AppLog.redactToken(hfToken)} " +
                "preferred_model_path=$preferredModelPath " +
                "fallback_relative_path=$fallbackRelativePath " +
                "auto_download_on_start=$autoDownloadOnStart"
        )

        return AppConfig(
            modelUrl = modelUrl,
            hfToken = hfToken,
            preferredModelPath = preferredModelPath,
            fallbackRelativePath = fallbackRelativePath,
            autoDownloadOnStart = autoDownloadOnStart,
        )
    }

    private fun parseSimpleYaml(text: String): Map<String, String> {
        val out = LinkedHashMap<String, String>()
        val lines = text.lineSequence()
        for (raw in lines) {
            val line = raw.trim()
            if (line.isBlank()) continue
            if (line.startsWith("#")) continue

            val idx = line.indexOf(':')
            if (idx <= 0) continue

            val key = line.substring(0, idx).trim()
            var value = line.substring(idx + 1).trim()

            if (value.startsWith('"') && value.endsWith('"') && value.length >= 2) {
                value = value.substring(1, value.length - 1)
            }

            out[key] = value
        }
        return out
    }

    private fun readConfigText(context: Context, assetName: String): String {
        val candidates = buildList {
            add(File("/data/local/tmp/functiongemma/$assetName"))
            val ext = context.getExternalFilesDir(null)
            if (ext != null) add(File(ext, assetName))
            add(File(context.filesDir, assetName))
        }

        AppLog.i("config.sources candidates=${candidates.joinToString { it.absolutePath }}")

        for (f in candidates) {
            if (f.exists() && f.isFile) {
                runCatching {
                    val t = f.readText()
                    AppLog.i("config.sources selected=${f.absolutePath} bytes=${t.length}")
                    return t
                }.onFailure { e ->
                    AppLog.w("config.sources failed_to_read=${f.absolutePath}", e)
                }
            }
        }

        val assetText = context.assets.open(assetName).bufferedReader().use { it.readText() }
        AppLog.i("config.sources selected=assets/$assetName bytes=${assetText.length}")
        return assetText
    }
}
