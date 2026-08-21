package com.simats.stainscope

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.simats.stainscope.data.SessionManager
import com.simats.stainscope.ui.analysis.AnalysisScreen
import com.simats.stainscope.ui.auth.*
import com.simats.stainscope.ui.compare.CompareScreen
import com.simats.stainscope.ui.dashboard.DashboardScreen
import com.simats.stainscope.ui.navigation.Screen
import com.simats.stainscope.ui.processing.ProcessingScreen
import com.simats.stainscope.ui.profile.ProfileScreen
import com.simats.stainscope.ui.profile.ProfileViewModel
import com.simats.stainscope.ui.reports.ReportsScreen
import com.simats.stainscope.ui.results.ResultsScreen
import com.simats.stainscope.ui.results.ResultsViewModel
import com.simats.stainscope.ui.theme.StainScopeTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val profileViewModel: ProfileViewModel = viewModel()
            val profileState by profileViewModel.uiState.collectAsState()
            
            StainScopeTheme(darkTheme = profileState.isDarkMode) {
                MainContent(profileViewModel)
            }
        }
    }
}

@Composable
fun MainContent(profileViewModel: ProfileViewModel) {
    val navController = rememberNavController()
    val context = LocalContext.current
    val sessionManager = SessionManager(context)
    val startDest = if (sessionManager.isLoggedIn()) Screen.Dashboard.route else Screen.Welcome.route
    
    // Shared navigation lambdas
    val goToDashboard = {
        navController.navigate(Screen.Dashboard.route) {
            popUpTo(0) { inclusive = true }
        }
    }
    val goToLogin = {
        navController.navigate(Screen.Login.route) {
            popUpTo(Screen.Welcome.route) { inclusive = false }
        }
    }
    val goToAnalysis = { 
        navController.navigate(Screen.Analysis.route) {
            launchSingleTop = true
        }
    }
    val goToCompare = { reportIds: String? -> 
        val route = if (reportIds != null) Screen.Compare.createRoute(reportIds) else Screen.Compare.route
        navController.navigate(route) {
            launchSingleTop = true
        }
    }
    val goToReports = { 
        navController.navigate(Screen.Reports.route) {
            launchSingleTop = true
        }
    }
    val goToProfile = { 
        navController.navigate(Screen.Profile.route) {
            launchSingleTop = true
        }
    }
    val goToResults = { sampleId: String -> 
        navController.navigate(Screen.Results.createRoute(sampleId)) 
    }
    val goToWelcome = {
        navController.navigate(Screen.Welcome.route) {
            popUpTo(0) { inclusive = true }
        }
    }

    NavHost(
        navController = navController,
        startDestination = startDest 
    ) {
        composable(Screen.Welcome.route) {
            WelcomeScreen(
                onNavigateToSignUp = { navController.navigate(Screen.SignUp.route) },
                onNavigateToLogin = { navController.navigate(Screen.Login.route) }
            )
        }
        composable(Screen.Login.route) {
            LoginScreen(
                onNavigateToSignUp = { navController.navigate(Screen.SignUp.route) },
                onNavigateToForgotPassword = { navController.navigate(Screen.ForgotPassword.route) },
                onLoginSuccess = goToDashboard
            )
        }
        composable(Screen.SignUp.route) {
            SignUpScreen(
                onNavigateToLogin = { navController.navigate(Screen.Login.route) },
                onSignUpSuccess = { 
                    navController.navigate(Screen.AccountCreated.route)
                }
            )
        }
        composable(Screen.ForgotPassword.route) {
            ForgotPasswordScreen(
                onNavigateToOtp = { email ->
                    navController.navigate(Screen.OtpVerification.createRoute(email))
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable(
            route = Screen.OtpVerification.route,
            arguments = listOf(navArgument("email") { type = NavType.StringType })
        ) { backStackEntry ->
            val email = backStackEntry.arguments?.getString("email") ?: ""
            OtpVerificationScreen(
                email = email,
                onVerifySuccess = { 
                    navController.navigate(Screen.ResetPassword.createRoute(email))
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable(
            route = Screen.ResetPassword.route,
            arguments = listOf(navArgument("email") { type = NavType.StringType })
        ) { backStackEntry ->
            val email = backStackEntry.arguments?.getString("email") ?: ""
            ResetPasswordScreen(
                email = email,
                onResetSuccess = goToLogin,
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable(Screen.AccountCreated.route) {
            AccountCreatedScreen(
                onGoToLogin = goToLogin
            )
        }
        composable(Screen.Dashboard.route) {
            DashboardScreen(
                onNavigateToAnalysis = goToAnalysis,
                onNavigateToCompare = { goToCompare(null) },
                onNavigateToReports = goToReports,
                onNavigateToProfile = goToProfile,
                onNavigateToResults = goToResults
            )
        }
        composable(Screen.Analysis.route) {
            AnalysisScreen(
                onNavigateToDashboard = goToDashboard,
                onNavigateToCompare = { goToCompare(null) },
                onNavigateToReports = goToReports,
                onNavigateToProfile = goToProfile,
                onNavigateBack = { navController.popBackStack() },
                onStartAnalysis = { uri, name, cellLine, treatment ->
                    navController.navigate(Screen.Processing.createRoute(uri.toString(), name, cellLine, treatment))
                }
            )
        }
        composable(
            route = Screen.Processing.route,
            arguments = listOf(
                navArgument("uri") { type = NavType.StringType },
                navArgument("name") { type = NavType.StringType },
                navArgument("cellLine") { type = NavType.StringType },
                navArgument("treatment") { type = NavType.StringType }
            )
        ) {
            val processingViewModel: com.simats.stainscope.ui.processing.ProcessingViewModel = viewModel()
            ProcessingScreen(
                onNavigateToDashboard = goToDashboard,
                onNavigateToCompare = { goToCompare(null) },
                onNavigateToReports = goToReports,
                onNavigateToProfile = goToProfile,
                onProcessingFinished = {
                    val targetId = processingViewModel.uiState.value.analysisId ?: ""
                    if (targetId.isNotEmpty()) {
                        navController.navigate(Screen.Results.createRoute(targetId)) {
                            popUpTo(Screen.Analysis.route) { inclusive = true }
                        }
                    }
                },
                viewModel = processingViewModel
            )
        }
        composable(
            route = Screen.Results.route,
            arguments = listOf(navArgument("sampleId") { type = NavType.StringType })
        ) { backStackEntry ->
            val sampleId = backStackEntry.arguments?.getString("sampleId") ?: ""
            val resultsViewModel: ResultsViewModel = viewModel()
            LaunchedEffect(sampleId) {
                if (sampleId.isNotEmpty()) {
                    resultsViewModel.loadAnalysisDetail(sampleId)
                }
            }
            ResultsScreen(
                onNavigateToDashboard = goToDashboard,
                onNavigateToAnalysis = goToAnalysis,
                onNavigateToCompare = { goToCompare(null) },
                onNavigateToReports = goToReports,
                onNavigateToProfile = goToProfile,
                onNavigateBack = { navController.popBackStack() },
                onCompareSample = { goToCompare(sampleId) },
                viewModel = resultsViewModel
            )
        }
        composable(
            route = Screen.Compare.route,
            arguments = listOf(navArgument("reportIds") { 
                type = NavType.StringType
                nullable = true
                defaultValue = null
            })
        ) {
            CompareScreen(
                onNavigateToDashboard = goToDashboard,
                onNavigateToAnalysis = goToAnalysis,
                onNavigateToReports = goToReports,
                onNavigateToProfile = goToProfile,
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable(Screen.Reports.route) {
            ReportsScreen(
                onNavigateToDashboard = goToDashboard,
                onNavigateToAnalysis = goToAnalysis,
                onNavigateToCompare = { goToCompare(it) },
                onNavigateToProfile = goToProfile,
                onNavigateBack = { navController.popBackStack() },
                onNavigateToResults = goToResults
            )
        }
        composable(Screen.Profile.route) {
            ProfileScreen(
                onNavigateToDashboard = goToDashboard,
                onNavigateToAnalysis = goToAnalysis,
                onNavigateToCompare = { goToCompare(null) },
                onNavigateToReports = goToReports,
                onNavigateToResults = goToResults,
                onNavigateBack = { navController.popBackStack() },
                onSignOut = {
                    profileViewModel.signOut()
                    goToWelcome()
                },
                viewModel = profileViewModel
            )
        }
    }
}
