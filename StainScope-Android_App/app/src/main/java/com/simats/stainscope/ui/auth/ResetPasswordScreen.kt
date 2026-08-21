package com.simats.stainscope.ui.auth

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.LockReset
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.simats.stainscope.ui.components.StainScopeButton
import com.simats.stainscope.ui.components.StainScopeTextField
import com.simats.stainscope.ui.theme.PrimaryMaroon
import com.simats.stainscope.ui.theme.TextGray

@Composable
fun ResetPasswordScreen(
    email: String,
    onResetSuccess: () -> Unit,
    onNavigateBack: () -> Unit
) {
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var visible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        visible = true
    }

    val missingRequirements = remember(password) {
        val list = mutableListOf<String>()
        if (!password.any { it.isUpperCase() }) list.add("an uppercase letter")
        if (!password.any { it.isLowerCase() }) list.add("a lowercase letter")
        if (!password.any { it.isDigit() }) list.add("a number")
        if (!password.any { !it.isLetterOrDigit() }) list.add("a special character")
        list
    }

    val isPasswordValid = missingRequirements.isEmpty() && password.isNotEmpty()

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
                        imageVector = Icons.Default.LockReset,
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
                    text = "Reset Password",
                    fontSize = 34.sp,
                    fontWeight = FontWeight.Black,
                    color = Color.Black,
                    lineHeight = 40.sp,
                    letterSpacing = (-1).sp
                )

                Text(
                    text = "Create a new strong password for your researcher account ($email).",
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
                    value = password,
                    onValueChange = { password = it },
                    label = "New Password",
                    placeholder = "••••••••",
                    isPassword = true
                )

                Spacer(modifier = Modifier.height(8.dp))
                
                // Dynamic Password Requirements
                if (password.isNotEmpty()) {
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
                    value = confirmPassword,
                    onValueChange = { confirmPassword = it },
                    label = "Confirm New Password",
                    placeholder = "••••••••",
                    isPassword = true
                )

                Spacer(modifier = Modifier.height(40.dp))

                StainScopeButton(
                    text = "Reset & Sign In",
                    onClick = onResetSuccess,
                    containerColor = if (isPasswordValid && password == confirmPassword) PrimaryMaroon else Color.Gray
                )
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600, 300))
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onNavigateBack() },
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = null,
                    tint = PrimaryMaroon,
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Back to Security Code",
                    color = PrimaryMaroon,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}
