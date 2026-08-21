package com.simats.stainscope.ui.navigation

import android.net.Uri

sealed class Screen(val route: String) {
    object Welcome : Screen("welcome")
    object Login : Screen("login")
    object SignUp : Screen("signup")
    object ForgotPassword : Screen("forgot_password")
    object OtpVerification : Screen("otp_verification/{email}") {
        fun createRoute(email: String) = "otp_verification/$email"
    }
    object ResetPassword : Screen("reset_password/{email}") {
        fun createRoute(email: String) = "reset_password/$email"
    }
    object AccountCreated : Screen("account_created")
    object Dashboard : Screen("dashboard")
    object Analysis : Screen("analysis")
    
    object Processing : Screen("processing/{uri}/{name}/{cellLine}/{treatment}") {
        fun createRoute(uri: String, name: String, cellLine: String, treatment: String): String {
            return "processing/${Uri.encode(uri)}/${Uri.encode(name)}/${Uri.encode(cellLine)}/${Uri.encode(treatment)}"
        }
    }

    object Results : Screen("results/{sampleId}") {
        fun createRoute(sampleId: String) = "results/$sampleId"
    }
    object Compare : Screen("compare?reportIds={reportIds}") {
        fun createRoute(reportIds: String) = "compare?reportIds=$reportIds"
    }
    object Reports : Screen("reports")
    object Profile : Screen("profile")
}
