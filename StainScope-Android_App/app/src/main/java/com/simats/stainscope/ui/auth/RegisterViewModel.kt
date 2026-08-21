package com.simats.stainscope.ui.auth

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.simats.stainscope.data.repository.StainScopeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class RegisterState(
    val name: String = "",
    val email: String = "",
    val password: String = "",
    val confirmPassword: String = "",
    val isRegisterEnabled: Boolean = false,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

class RegisterViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = StainScopeRepository(application)

    private val _uiState = MutableStateFlow(RegisterState())
    val uiState: StateFlow<RegisterState> = _uiState.asStateFlow()

    fun onNameChange(name: String) {
        _uiState.update { it.copy(name = name, errorMessage = null) }
        validate()
    }

    fun onEmailChange(email: String) {
        _uiState.update { it.copy(email = email, errorMessage = null) }
        validate()
    }

    fun onPasswordChange(password: String) {
        _uiState.update { it.copy(password = password, errorMessage = null) }
        validate()
    }

    fun onConfirmPasswordChange(confirmPassword: String) {
        _uiState.update { it.copy(confirmPassword = confirmPassword, errorMessage = null) }
        validate()
    }

    private fun validate() {
        val state = _uiState.value
        val isEmailValid = state.email.contains("@")
        val passwordsMatch = state.password == state.confirmPassword && state.password.isNotEmpty()
        _uiState.update { it.copy(isRegisterEnabled = isEmailValid && passwordsMatch && state.name.isNotEmpty()) }
    }

    fun signUp(onSuccess: () -> Unit, onError: (String) -> Unit) {
        val email = _uiState.value.email.trim()
        val password = _uiState.value.password
        val name = _uiState.value.name.trim()

        _uiState.update { it.copy(isLoading = true, errorMessage = null) }

        viewModelScope.launch {
            try {
                val result = repository.signUp(email, password, name)
                result.fold(
                    onSuccess = {
                        _uiState.update { it.copy(isLoading = false) }
                        onSuccess()
                    },
                    onFailure = { error ->
                        val msg = error.message ?: "Sign up failed. Please try again."
                        _uiState.update { it.copy(isLoading = false, errorMessage = msg) }
                        onError(msg)
                    }
                )
            } catch (e: Exception) {
                val msg = e.message ?: "Unexpected error during registration."
                _uiState.update { it.copy(isLoading = false, errorMessage = msg) }
                onError(msg)
            }
        }
    }
}
