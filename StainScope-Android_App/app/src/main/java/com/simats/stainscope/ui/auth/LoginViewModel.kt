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

data class LoginState(
    val email: String = "",
    val password: String = "",
    val isLoginEnabled: Boolean = false,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

class LoginViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = StainScopeRepository(application)

    private val _uiState = MutableStateFlow(LoginState())
    val uiState: StateFlow<LoginState> = _uiState.asStateFlow()

    fun onEmailChange(email: String) {
        _uiState.update { it.copy(email = email, errorMessage = null) }
        validate()
    }

    fun onPasswordChange(password: String) {
        _uiState.update { it.copy(password = password, errorMessage = null) }
        validate()
    }

    private fun validate() {
        val state = _uiState.value
        val isValid = state.email.contains("@") && state.password.isNotEmpty()
        _uiState.update { it.copy(isLoginEnabled = isValid) }
    }

    fun login(onSuccess: () -> Unit, onError: (String) -> Unit) {
        val email = _uiState.value.email.trim()
        val password = _uiState.value.password
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }

        viewModelScope.launch {
            try {
                val result = repository.signIn(email, password)
                result.fold(
                    onSuccess = {
                        _uiState.update { it.copy(isLoading = false) }
                        onSuccess()
                    },
                    onFailure = { error ->
                        val msg = error.message ?: "Authentication failed. Invalid credentials or network error."
                        _uiState.update { it.copy(isLoading = false, errorMessage = msg) }
                        onError(msg)
                    }
                )
            } catch (e: Exception) {
                val msg = e.message ?: "Unexpected error during login."
                _uiState.update { it.copy(isLoading = false, errorMessage = msg) }
                onError(msg)
            }
        }
    }
}
