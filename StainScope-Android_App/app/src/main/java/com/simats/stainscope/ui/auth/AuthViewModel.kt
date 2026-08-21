package com.simats.stainscope.ui.auth

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class AuthViewModel : ViewModel() {
    // Shared or individual states can be managed here.
    // For now, keeping it simple as requested for placeholder data.

    private val _email = MutableStateFlow("")
    val email: StateFlow<String> = _email.asStateFlow()

    fun onEmailChange(newValue: String) {
        _email.value = newValue
    }

    // Add other fields as needed for placeholder logic
}
