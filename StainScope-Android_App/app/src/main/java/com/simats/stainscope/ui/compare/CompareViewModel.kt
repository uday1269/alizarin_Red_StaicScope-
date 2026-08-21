package com.simats.stainscope.ui.compare

import android.app.Application
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.viewModelScope
import com.simats.stainscope.data.repository.StainScopeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ReportSummary(
    val id: String,
    val name: String,
    val area: String,
    val od: String,
    val nodes: String,
    val day: String,
    val dayColor: Color
)

data class CompareSample(
    val id: String,
    val name: String,
    val cellLine: String = "hMSC",
    val timeline: String = "Day 14",
    val treatment: String = "Standard Basal",
    val magnification: String = "20x Objective",
    val mineralizedArea: String,
    val stainIntensity: String,
    val noduleCount: String,
    val avgNoduleSize: String,
    val calciumDensity: String,
    val aiConfidence: String
)

enum class CompareInspectionMode { Original, Segmentation, Heatmap }

data class CompareState(
    val availableReports: List<ReportSummary> = emptyList(),
    val selectedReportIds: Set<String> = emptySet(),
    val selectedSamples: List<CompareSample> = emptyList(),
    val isComparing: Boolean = false,
    val overlayOpacity: Float = 0.85f,
    val zoom: Float = 1.0f,
    val inspectionMode: CompareInspectionMode = CompareInspectionMode.Segmentation,
    val isLoading: Boolean = false
)

class CompareViewModel(
    application: Application,
    savedStateHandle: SavedStateHandle
) : AndroidViewModel(application) {
    private val repository = StainScopeRepository(application)

    private val _uiState = MutableStateFlow(CompareState())
    val uiState: StateFlow<CompareState> = _uiState.asStateFlow()

    private val passedReportIds: String? = savedStateHandle["reportIds"]

    init {
        loadData()
    }

    fun loadData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            val res = repository.listAnalyses()
            res.getOrNull()?.let { list ->
                val summaries = list.map { item ->
                    val areaStr = if (item.mineralizedAreaPercent != null) String.format("%.1f%%", item.mineralizedAreaPercent) else "0.0%"
                    val odStr = (item.opticalDensity ?: item.opticalDensityProxy)?.let { String.format("%.2f", it) } ?: "0.00"
                    val nodesStr = item.noduleCount?.toString() ?: "0"
                    ReportSummary(
                        id = item.id,
                        name = item.sampleTitle ?: "Sample ${item.id.take(6)}",
                        area = areaStr,
                        od = odStr,
                        nodes = nodesStr,
                        day = "Day 14",
                        dayColor = Color(0xFFE8F5E9)
                    )
                }

                // Handle passed IDs from navigation
                val initialSelectedIds = if (!passedReportIds.isNullOrEmpty()) {
                    passedReportIds.split(",").toSet()
                } else {
                    summaries.take(2).map { it.id }.toSet()
                }

                _uiState.value = _uiState.value.copy(
                    availableReports = summaries,
                    selectedReportIds = initialSelectedIds,
                    isLoading = false
                )
                updateSelectedSamples(initialSelectedIds)
            } ?: run {
                _uiState.value = _uiState.value.copy(isLoading = false)
            }
        }
    }

    fun toggleReportSelection(reportId: String) {
        val currentSelected = _uiState.value.selectedReportIds
        val newSelected = if (currentSelected.contains(reportId)) {
            currentSelected - reportId
        } else {
            currentSelected + reportId
        }
        _uiState.value = _uiState.value.copy(selectedReportIds = newSelected)
        updateSelectedSamples(newSelected)
    }

    private fun updateSelectedSamples(selectedIds: Set<String>) {
        val samples = _uiState.value.availableReports.filter { selectedIds.contains(it.id) }.map { rep ->
            CompareSample(
                id = rep.id,
                name = rep.name,
                mineralizedArea = rep.area,
                stainIntensity = "${rep.od} OD",
                noduleCount = rep.nodes,
                avgNoduleSize = "14.5 μm²",
                calciumDensity = "64.2 μg/cm²",
                aiConfidence = "99.1%"
            )
        }
        _uiState.value = _uiState.value.copy(selectedSamples = samples, isComparing = samples.isNotEmpty())
    }

    fun startComparison() {
        val selected = _uiState.value.selectedReportIds.toList()
        if (selected.isNotEmpty()) {
            _uiState.value = _uiState.value.copy(isComparing = true)
            viewModelScope.launch {
                repository.createSavedComparison(
                    title = "Comparison ${selected.joinToString(",") { it.take(4) }}",
                    analysisIds = selected
                )
            }
        }
    }

    fun setInspectionMode(mode: CompareInspectionMode) {
        _uiState.value = _uiState.value.copy(inspectionMode = mode)
    }
}
