package com.simats.stainscope.ui.auth

import android.widget.Toast
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Science
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.simats.stainscope.ui.components.GoogleSignInButton
import com.simats.stainscope.ui.components.StainScopeButton
import com.simats.stainscope.ui.components.StainScopeTextField
import com.simats.stainscope.ui.theme.PrimaryMaroon
import com.simats.stainscope.ui.theme.TextGray

@Composable
fun LoginScreen(
    onNavigateToSignUp: () -> Unit,
    onNavigateToForgotPassword: () -> Unit,
    onLoginSuccess: () -> Unit,
    viewModel: LoginViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var visible by remember { mutableStateOf(false) }
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        visible = true
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .padding(horizontal = 24.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.Start
    ) {
        Spacer(modifier = Modifier.height(60.dp))

        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600)) + slideInVertically(initialOffsetY = { -20 })
        ) {
            Surface(
                modifier = Modifier.size(56.dp),
                shape = RoundedCornerShape(16.dp),
                color = PrimaryMaroon.copy(alpha = 0.08f)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = Icons.Default.Science,
                        contentDescription = null,
                        tint = PrimaryMaroon,
                        modifier = Modifier.size(28.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600, 100)) + slideInVertically(initialOffsetY = { 20 })
        ) {
            Column {
                Text(
                    text = "Welcome Back",
                    fontSize = 34.sp,
                    fontWeight = FontWeight.Black,
                    color = Color.Black,
                    lineHeight = 40.sp,
                    letterSpacing = (-1).sp
                )

                Text(
                    text = "Sign in to access your lab reports and continue your research.",
                    fontSize = 16.sp,
                    color = TextGray,
                    modifier = Modifier.padding(top = 12.dp),
                    lineHeight = 22.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(48.dp))

        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600, 200)) + slideInVertically(initialOffsetY = { 20 })
        ) {
            Column {
                StainScopeTextField(
                    value = uiState.email,
                    onValueChange = viewModel::onEmailChange,
                    label = "Email Address",
                    placeholder = "Enter the email"
                )

                Spacer(modifier = Modifier.height(20.dp))

                StainScopeTextField(
                    value = uiState.password,
                    onValueChange = viewModel::onPasswordChange,
                    label = "Password",
                    placeholder = "Enter the password",
                    isPassword = true
                )

                Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.CenterEnd) {
                    Text(
                        text = "Forgot Password?",
                        color = PrimaryMaroon,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier
                            .padding(vertical = 16.dp)
                            .clickable { onNavigateToForgotPassword() }
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                StainScopeButton(
                    text = if (uiState.isLoading) "Signing In..." else "Sign In",
                    onClick = {
                        when {
                            uiState.email.isEmpty() -> {
                                Toast.makeText(context, "fill email", Toast.LENGTH_SHORT).show()
                            }
                            !uiState.email.contains("@") -> {
                                Toast.makeText(context, "Enter correct email", Toast.LENGTH_SHORT).show()
                            }
                            uiState.password.isEmpty() -> {
                                Toast.makeText(context, "fill password", Toast.LENGTH_SHORT).show()
                            }
                            else -> {
                                viewModel.login(
                                    onSuccess = onLoginSuccess,
                                    onError = { errMsg ->
                                        Toast.makeText(context, errMsg, Toast.LENGTH_LONG).show()
                                    }
                                )
                            }
                        }
                    }
                )
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600, 300))
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    HorizontalDivider(modifier = Modifier.weight(1f), color = Color(0xFFEEEEEE))
                    Text(
                        text = "OR CONTINUE WITH",
                        modifier = Modifier.padding(horizontal = 16.dp),
                        color = TextGray,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.sp
                    )
                    HorizontalDivider(modifier = Modifier.weight(1f), color = Color(0xFFEEEEEE))
                }

                Spacer(modifier = Modifier.height(24.dp))

                GoogleSignInButton(onClick = { /* Handle Google Sign In */ })

                Spacer(modifier = Modifier.height(48.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = "New to StainScope? ",
                        color = TextGray,
                        fontSize = 15.sp
                    )
                    Text(
                        text = "Join now",
                        color = PrimaryMaroon,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Black,
                        modifier = Modifier.clickable { onNavigateToSignUp() }
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(40.dp))
    }
}
