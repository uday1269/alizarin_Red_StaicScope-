package com.simats.stainscope.ui.auth

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Key
import androidx.compose.material.icons.filled.LockOpen
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.simats.stainscope.ui.components.StainScopeButton
import com.simats.stainscope.ui.theme.GoogleButtonBorder
import com.simats.stainscope.ui.theme.PrimaryMaroon
import com.simats.stainscope.ui.theme.TextGray

@Composable
fun OtpVerificationScreen(
    email: String,
    onVerifySuccess: () -> Unit,
    onNavigateBack: () -> Unit
) {
    var otpValues = remember { mutableStateListOf("", "", "", "") }
    var visible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        visible = true
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .padding(horizontal = 24.dp),
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
                        imageVector = Icons.Default.LockOpen,
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
                    text = "Verify Identity",
                    fontSize = 34.sp,
                    fontWeight = FontWeight.Black,
                    color = Color.Black,
                    lineHeight = 40.sp,
                    letterSpacing = (-1).sp
                )

                Text(
                    text = buildAnnotatedString {
                        append("We've sent a research authentication code to ")
                        withStyle(style = SpanStyle(fontWeight = FontWeight.Bold, color = PrimaryMaroon)) {
                            append(email)
                        }
                    },
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
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    otpValues.forEachIndexed { index, value ->
                        OtpBox(
                            value = value,
                            onValueChange = { newValue ->
                                if (newValue.length <= 1) {
                                    otpValues[index] = newValue
                                }
                            },
                            modifier = Modifier.weight(1f)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = "Didn't receive code? ",
                        color = TextGray,
                        fontSize = 15.sp
                    )
                    Text(
                        text = "Resend (0:45)",
                        color = PrimaryMaroon,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Black,
                        modifier = Modifier.clickable { /* Handle Resend */ }
                    )
                }

                Spacer(modifier = Modifier.height(40.dp))

                StainScopeButton(
                    text = "Verify & Access",
                    onClick = onVerifySuccess
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
                    text = "Return to Previous Step",
                    color = PrimaryMaroon,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
fun OtpBox(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier.height(68.dp),
        shape = RoundedCornerShape(16.dp),
        textStyle = LocalTextStyle.current.copy(
            textAlign = TextAlign.Center,
            fontSize = 28.sp,
            fontWeight = FontWeight.Black,
            color = Color.Black
        ),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
        singleLine = true,
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = PrimaryMaroon,
            unfocusedBorderColor = Color(0xFFEEEEEE),
            focusedContainerColor = PrimaryMaroon.copy(alpha = 0.02f),
            unfocusedContainerColor = Color(0xFFFAFAFA),
            cursorColor = PrimaryMaroon
        )
    )
}
