package com.simats.stainscope.ui.auth

import android.widget.Toast
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Science
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
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
fun SignUpScreen(
    onNavigateToLogin: () -> Unit,
    onSignUpSuccess: (String) -> Unit,
    viewModel: RegisterViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var visible by remember { mutableStateOf(false) }
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        visible = true
    }

    val missingRequirements = remember(uiState.password) {
        val list = mutableListOf<String>()
        if (!uiState.password.any { it.isUpperCase() }) list.add("an uppercase letter")
        if (!uiState.password.any { it.isLowerCase() }) list.add("a lowercase letter")
        if (!uiState.password.any { it.isDigit() }) list.add("a number")
        if (!uiState.password.any { !it.isLetterOrDigit() }) list.add("a special character")
        list
    }

    val isPasswordValid = missingRequirements.isEmpty() && uiState.password.isNotEmpty()

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
                    text = "Create Account",
                    fontSize = 34.sp,
                    fontWeight = FontWeight.Black,
                    color = Color.Black,
                    lineHeight = 40.sp,
                    letterSpacing = (-1).sp
                )

                Text(
                    text = "Start your automated stain quantification journey with our AI engine.",
                    fontSize = 16.sp,
                    color = TextGray,
                    modifier = Modifier.padding(top = 12.dp),
                    lineHeight = 22.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(40.dp))

        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600, 200)) + slideInVertically(initialOffsetY = { 20 })
        ) {
            Column {
                StainScopeTextField(
                    value = uiState.name,
                    onValueChange = viewModel::onNameChange,
                    label = "Full Name",
                    placeholder = "Enter name"
                )

                Spacer(modifier = Modifier.height(20.dp))

                StainScopeTextField(
                    value = uiState.email,
                    onValueChange = viewModel::onEmailChange,
                    label = "Email Address",
                    placeholder = "Enter email"
                )

                Spacer(modifier = Modifier.height(20.dp))

                StainScopeTextField(
                    value = uiState.password,
                    onValueChange = viewModel::onPasswordChange,
                    label = "Password",
                    placeholder = "Enter password",
                    isPassword = true
                )

                Spacer(modifier = Modifier.height(8.dp))
                
                // Dynamic Password Requirements
                if (uiState.password.isNotEmpty()) {
                    Text(
                        text = if (isPasswordValid) {
                            "Password requirements met ✓"
                        } else {
                            "Add " + missingRequirements.joinToString(
                                separator = if (missingRequirements.size > 2) ", " else " and ",
                                transform = { it }
                            ).replace(Regex(", ([^,]+)$"), " and $1")
                        },
                        fontSize = 13.sp,
                        color = if (isPasswordValid) Color(0xFF2E7D32) else PrimaryMaroon,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.padding(start = 4.dp)
                    )
                }

                Spacer(modifier = Modifier.height(20.dp))

                StainScopeTextField(
                    value = uiState.confirmPassword,
                    onValueChange = viewModel::onConfirmPasswordChange,
                    label = "Confirm Password",
                    placeholder = "Re-enter password",
                    isPassword = true
                )

                Spacer(modifier = Modifier.height(40.dp))

                StainScopeButton(
                    text = if (uiState.isLoading) "Creating Account..." else "Create Account",
                    onClick = {
                        when {
                            uiState.name.isEmpty() -> {
                                Toast.makeText(context, "fill name", Toast.LENGTH_SHORT).show()
                            }
                            uiState.email.isEmpty() -> {
                                Toast.makeText(context, "fill email", Toast.LENGTH_SHORT).show()
                            }
                            !uiState.email.contains("@") -> {
                                Toast.makeText(context, "Enter correct email", Toast.LENGTH_SHORT).show()
                            }
                            uiState.password.isEmpty() -> {
                                Toast.makeText(context, "fill password", Toast.LENGTH_SHORT).show()
                            }
                            !isPasswordValid -> {
                                Toast.makeText(context, "Enter correct password", Toast.LENGTH_SHORT).show()
                            }
                            uiState.confirmPassword.isEmpty() -> {
                                Toast.makeText(context, "fill confirm password", Toast.LENGTH_SHORT).show()
                            }
                            uiState.password != uiState.confirmPassword -> {
                                Toast.makeText(context, "Passwords do not match", Toast.LENGTH_SHORT).show()
                            }
                            else -> {
                                viewModel.signUp(
                                    onSuccess = { onSignUpSuccess(uiState.email) },
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
                        text = "OR SIGN UP WITH",
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
                        text = "Already have an account? ",
                        color = TextGray,
                        fontSize = 15.sp
                    )
                    Text(
                        text = "Sign In",
                        color = PrimaryMaroon,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Black,
                        modifier = Modifier.clickable { onNavigateToLogin() }
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(40.dp))
    }
}
