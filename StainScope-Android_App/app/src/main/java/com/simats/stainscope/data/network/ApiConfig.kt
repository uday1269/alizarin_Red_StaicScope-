package com.simats.stainscope.data.network

import android.os.Build

object ApiConfig {
    val isEmulator: Boolean
        get() = (Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MODEL.contains("Android SDK built for x86")
                || Build.MANUFACTURER.contains("Genymotion")
                || Build.HARDWARE.contains("goldfish")
                || Build.HARDWARE.contains("ranchu")
                || Build.PRODUCT.contains("sdk_gphone")
                || Build.PRODUCT.contains("google_sdk")
                || Build.PRODUCT.contains("vbox")
                || Build.BOARD.lowercase().contains("goldfish")
                || (Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic")))

    var FASTAPI_BASE_URL: String = if (isEmulator) "http://10.0.2.2:8000/" else "http://10.131.43.110:8000/"
}
