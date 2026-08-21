package com.simats.stainscope.ui.analysis

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

data class AnalysisState(
    val sampleFileName: String = "",
    val cellLine: String = "hMSC (Human Mesenchymal Stem Cells)",
    val incubationPeriod: String = "Day 21",
    val magnification: String = "20x Objective",
    val selectedImageUri: Uri? = null,
    val isLoading: Boolean = false,
    val isSuccess: Boolean = false,
    val error: String? = null
)

class AnalysisViewModel(application: Application) : AndroidViewModel(application) {
    private val _uiState = MutableStateFlow(AnalysisState())
    val uiState: StateFlow<AnalysisState> = _uiState.asStateFlow()

    fun onFileNameChange(newName: String) {
        _uiState.update { it.copy(sampleFileName = newName) }
    }

    fun onCellLineChange(value: String) {
        _uiState.update { it.copy(cellLine = value) }
    }

    fun onIncubationPeriodChange(value: String) {
        _uiState.update { it.copy(incubationPeriod = value) }
    }

    fun onMagnificationChange(value: String) {
        _uiState.update { it.copy(magnification = value) }
    }

    fun onImageSelected(uri: Uri?) {
        _uiState.update { it.copy(selectedImageUri = uri) }
        uri?.lastPathSegment?.let { fileName ->
            val cleanName = if (fileName.contains(":")) fileName.substringAfterLast(":") else fileName
            onFileNameChange(cleanName)
        }
    }

    fun startAnalysis() {
        val state = _uiState.value
        if (state.selectedImageUri == null) {
            _uiState.update { it.copy(error = "Please select an image first") }
            return
        }
        if (state.sampleFileName.isBlank()) {
            _uiState.update { it.copy(error = "Experiment name cannot be empty") }
            return
        }
        _uiState.update { it.copy(isSuccess = true) }
    }

    fun resetState() {
        _uiState.update { it.copy(isSuccess = false, isLoading = false, error = null) }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
