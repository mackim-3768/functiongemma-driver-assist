package com.functiongemma.driverassist

import android.util.Log

object AppLog {
    const val TAG: String = "FunctionGemmaDriverAsst"

    fun d(message: String) {
        Log.d(TAG, message)
    }

    fun i(message: String) {
        Log.i(TAG, message)
    }

    fun w(message: String, t: Throwable? = null) {
        if (t != null) {
            Log.w(TAG, message, t)
        } else {
            Log.w(TAG, message)
        }
    }

    fun e(message: String, t: Throwable? = null) {
        if (t != null) {
            Log.e(TAG, message, t)
        } else {
            Log.e(TAG, message)
        }
    }

    fun redactToken(token: String): String {
        val t = token.trim()
        if (t.isBlank()) return "(blank)"
        if (t.length <= 8) return "***"
        return t.take(4) + "…" + t.takeLast(4)
    }

    fun summarizeUrl(url: String): String {
        val u = url.trim()
        if (u.isBlank()) return "(blank)"
        return if (u.length <= 160) u else u.take(160) + "…"
    }
}
