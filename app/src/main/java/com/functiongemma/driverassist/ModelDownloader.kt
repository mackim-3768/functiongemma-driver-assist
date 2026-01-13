package com.functiongemma.driverassist

import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL

object ModelDownloader {

    data class Progress(
        val bytesDownloaded: Long,
        val bytesTotal: Long,
    ) {
        val fraction: Float?
            get() = if (bytesTotal > 0) bytesDownloaded.toFloat() / bytesTotal.toFloat() else null
    }

    fun downloadToFile(
        url: String,
        hfToken: String,
        destFile: File,
        onProgress: (Progress) -> Unit,
    ) {
        AppLog.i(
            "model.download start url=${AppLog.summarizeUrl(url)} " +
                "hf_token=${AppLog.redactToken(hfToken)} dest=${destFile.absolutePath}"
        )
        destFile.parentFile?.mkdirs()

        val tmpFile = File(destFile.absolutePath + ".tmp")
        if (tmpFile.exists()) tmpFile.delete()

        val conn = (URL(url).openConnection() as HttpURLConnection).apply {
            connectTimeout = 20_000
            readTimeout = 60_000
            requestMethod = "GET"
            setRequestProperty("Accept", "application/octet-stream")
            if (hfToken.isNotBlank()) {
                setRequestProperty("Authorization", "Bearer $hfToken")
            }
        }

        try {
            val code = conn.responseCode
            AppLog.i(
                "model.download http_response code=$code " +
                    "message=${conn.responseMessage} content_length=${conn.contentLengthLong}"
            )
            if (code !in 200..299) {
                val err = runCatching { conn.errorStream?.bufferedReader()?.use { it.readText() } }.getOrNull().orEmpty()
                AppLog.w("model.download http_error code=$code message=${conn.responseMessage} err_len=${err.length}")
                throw IllegalStateException("HTTP $code ${conn.responseMessage}. $err".trim())
            }

            val total = conn.contentLengthLong
            var downloaded = 0L

            conn.inputStream.use { input ->
                FileOutputStream(tmpFile).use { output ->
                    val buf = ByteArray(256 * 1024)
                    while (true) {
                        val read = input.read(buf)
                        if (read <= 0) break
                        output.write(buf, 0, read)
                        downloaded += read
                        onProgress(Progress(bytesDownloaded = downloaded, bytesTotal = total))
                    }
                    output.flush()
                }
            }

            AppLog.i("model.download finished bytes=$downloaded tmp=${tmpFile.absolutePath}")

            if (destFile.exists()) destFile.delete()
            if (!tmpFile.renameTo(destFile)) {
                throw IllegalStateException("Failed to move downloaded file into place")
            }

            AppLog.i("model.download done dest=${destFile.absolutePath} bytes=${destFile.length()}")
        } finally {
            conn.disconnect()
            if (tmpFile.exists() && !destFile.exists()) {
                tmpFile.delete()
                AppLog.i("model.download cleanup_deleted_tmp tmp=${tmpFile.absolutePath}")
            }
        }
    }
}
