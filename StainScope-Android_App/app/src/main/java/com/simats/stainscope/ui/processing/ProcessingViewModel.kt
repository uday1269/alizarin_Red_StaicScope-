package com.simats.stainscope.ui.processing

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.viewModelScope
import com.simats.stainscope.data.repository.StainScopeRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ProcessingStep(
    val id: Int,
    val title: String,
    val description: String,
    val isCompleted: Boolean = false,
    val isProcessing: Boolean = false
)

data class ProcessingState(
    val progress: Int = 0,
    val currentStage: String = "Initializing Analysis...",
    val estimatedRemaining: String = "3s",
    val analysisId: String? = null,
    val steps: List<ProcessingStep> = listOf(
        ProcessingStep(1, "1. Image Loading & Buffer Validation", "Ingesting micrograph buffer into GPU memory..."),
        ProcessingStep(2, "2. Preprocessing & Illumination Alignment", "Calibrating illumination variations and white balance across matrix..."),
        ProcessingStep(3, "3. HSV Color Channel Extraction (560nm)", "Filtering Alizarin Red S spectral absorbance peak wavelengths..."),
        ProcessingStep(4, "4. AI Nodule Segmentation & Contour Mapping", "Isolating mineralized node clusters and extracting centroid coordinates..."),
        ProcessingStep(5, "5. Mineralization & Calcium Quantification", "Calculating surface area fraction (%) and calcium density (μg/cm²)..."),
        ProcessingStep(6, "6. Automatic Report & AI Conclusion Synthesis", "Generating clinical report interpretation and PDF data payload...")
    )
)

class ProcessingViewModel(
    application: Application,
    savedStateHandle: SavedStateHandle
) : AndroidViewModel(application) {
    private val repository = StainScopeRepository(application)
    private val _uiState = MutableStateFlow(ProcessingState())
    val uiState: StateFlow<ProcessingState> = _uiState.asStateFlow()

    private val _isFinished = MutableStateFlow(false)
    val isFinished: StateFlow<Boolean> = _isFinished.asStateFlow()

    private val imageUri: String? = savedStateHandle["uri"]
    private val sampleName: String? = savedStateHandle["name"]
    private val cellLine: String? = savedStateHandle["cellLine"]
    private val treatment: String? = savedStateHandle["treatment"]

    init {
        startProcessing()
    }

    private fun startProcessing() {
        viewModelScope.launch {
            val totalSteps = _uiState.value.steps.size
            
            // 1. Perform actual analysis call
            var resultAnalysisId: String? = null
            var processingError: String? = null

            val analysisJob = launch {
                try {
                    val uri = imageUri?.let { Uri.parse(it) }
                    if (uri != null) {
                        val inputStream = getApplication<Application>().contentResolver.openInputStream(uri)
                        val bytes = inputStream?.readBytes()
                        inputStream?.close()

                        if (bytes != null) {
                            val res = repository.analyzeImage(
                                imageBytes = bytes,
                                fileName = sampleName ?: "micrograph.png",
                                sampleTitle = sampleName,
                                cellLine = cellLine,
                                treatment = treatment
                            )
                            res.getOrNull()?.let { dto ->
                                resultAnalysisId = dto.id ?: dto.analysisId
                            }
                            if (res.isFailure) {
                                processingError = res.exceptionOrNull()?.message ?: "Backend analysis failed"
                            }
                        } else {
                            processingError = "Failed to read image buffer"
                        }
                    } else {
                        processingError = "No image selected"
                    }
                } catch (e: Exception) {
                    android.util.Log.e("ProcessingViewModel", "Error in analysis pipeline", e)
                    processingError = e.localizedMessage ?: "Error during processing"
                }
            }

            // 2. Update stage animations
            for (i in 0 until totalSteps) {
                updateStep(i, isProcessing = true, isCompleted = false)
                
                val stepDuration = 500L
                val progressIncrement = 100 / totalSteps
                
                repeat(5) {
                    delay(stepDuration / 5)
                    _uiState.value = _uiState.value.copy(progress = _uiState.value.progress + (progressIncrement / 5))
                }

                updateStep(i, isProcessing = false, isCompleted = true)
            }

            // Ensure analysis call is finished before moving on
            analysisJob.join()

            if (processingError != null && resultAnalysisId == null) {
                android.util.Log.e("ProcessingViewModel", "Analysis pipeline finished with error: $processingError")
            }

            _uiState.value = _uiState.value.copy(
                progress = 100,
                currentStage = if (resultAnalysisId != null) "Analysis Complete" else "Analysis Finished",
                estimatedRemaining = "0s",
                analysisId = resultAnalysisId
            )
            delay(500)
            _isFinished.value = true
        }
    }

    private fun updateStep(index: Int, isProcessing: Boolean, isCompleted: Boolean) {
        val newSteps = _uiState.value.steps.toMutableList()
        if (index < newSteps.size) {
            val step = newSteps[index]
            newSteps[index] = step.copy(isProcessing = isProcessing, isCompleted = isCompleted)
            _uiState.value = _uiState.value.copy(steps = newSteps)
        }
    }
}
