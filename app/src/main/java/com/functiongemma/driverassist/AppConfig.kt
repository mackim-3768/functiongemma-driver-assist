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
        val text = readConfigText(context = context, assetName = assetName)
        val map = parseSimpleYaml(text)

        return AppConfig(
            modelUrl = map["model_url"].orEmpty(),
            hfToken = map["hf_token"].orEmpty(),
            preferredModelPath = map["preferred_model_path"].orEmpty(),
            fallbackRelativePath = map["fallback_relative_path"].orEmpty(),
            autoDownloadOnStart = map["auto_download_on_start"].toBooleanStrictOrNull() ?: false,
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

        for (f in candidates) {
            if (f.exists() && f.isFile) {
                runCatching { return f.readText() }
            }
        }

        return context.assets.open(assetName).bufferedReader().use { it.readText() }
    }
}
