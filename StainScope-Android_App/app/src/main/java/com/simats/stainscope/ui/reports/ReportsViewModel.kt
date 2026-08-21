package com.simats.stainscope.ui.reports

import android.app.Application
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.simats.stainscope.data.repository.StainScopeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.Locale

data class ReportItem(
    val id: String,
    val name: String,
    val date: String,
    val magnification: String = "20x Objective",
    val mineralizedArea: String,
    val mineralizedAreaValue: Double = 0.0,
    val stainIntensity: String,
    val calciumDensity: String,
    val noduleCount: String,
    val status: String,
    val statusColor: Color,
    val isSelected: Boolean = false
)

data class ReportsState(
    val searchQuery: String = "",
    val selectedFilter: String = "All Reports",
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val errorMessage: String? = null,
    val reports: List<ReportItem> = emptyList()
) {
    val filteredReports: List<ReportItem>
        get() {
            var list = reports
            if (selectedFilter != "All Reports") {
                list = when (selectedFilter) {
                    "High Mineralization" -> list.filter { it.status == "High Mineralization" }
                    "Moderate Mineralization" -> list.filter { it.status == "Moderate Mineralization" }
                    "Low Mineralization" -> list.filter { it.status == "Low Mineralization" }
                    else -> list
                }
            }
            if (searchQuery.isNotBlank()) {
                val q = searchQuery.trim().lowercase(Locale.US)
                list = list.filter {
                    it.name.lowercase(Locale.US).contains(q) ||
                    it.id.lowercase(Locale.US).contains(q) ||
                    it.status.lowercase(Locale.US).contains(q) ||
                    it.magnification.lowercase(Locale.US).contains(q)
                }
            }
            return list
        }
}

class ReportsViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = StainScopeRepository(application)

    private val _uiState = MutableStateFlow(ReportsState())
    val uiState: StateFlow<ReportsState> = _uiState.asStateFlow()

    init {
        loadUserAnalyses()
    }

    fun loadUserAnalyses(isRefresh: Boolean = false) {
        viewModelScope.launch {
            if (isRefresh) {
                _uiState.update { it.copy(isRefreshing = true, errorMessage = null) }
            } else {
                _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            }
            val res = repository.listAnalyses()
            res.getOrNull()?.let { list ->
                val items = list.map { dto ->
                    val areaVal = dto.mineralizedAreaPercent ?: 0.0
                    val areaStr = String.format(Locale.US, "%.2f%%", areaVal)
                    val odVal = dto.opticalDensity ?: dto.opticalDensityProxy ?: 0.0
                    val odStr = String.format(Locale.US, "%.2f OD", odVal)
                    val calcVal = dto.calciumDensityUgCm2 ?: (areaVal * 0.05)
                    val calcStr = String.format(Locale.US, "%.2f µg/cm²", calcVal)
                    val countStr = dto.noduleCount?.let { String.format(Locale.US, "%,d", it) } ?: "0"
                    val rawDate = dto.analyzedAt ?: dto.createdAt
                    val dateStr = rawDate?.take(16)?.replace("T", " ") ?: "Recent"
                    val titleStr = dto.sampleTitle?.ifEmpty { null } ?: "ARS Micrograph (${dto.id.take(8)})"
                    
                    val (statusText, statusColor) = when {
                        areaVal > 50.0 -> "High Mineralization" to Color(0xFF059669)
                        areaVal > 20.0 -> "Moderate Mineralization" to Color(0xFFD97706)
                        else -> "Low Mineralization" to Color(0xFF64748B)
                    }

                    ReportItem(
                        id = dto.id,
                        name = titleStr,
                        date = dateStr,
                        mineralizedArea = areaStr,
                        mineralizedAreaValue = areaVal,
                        stainIntensity = odStr,
                        calciumDensity = calcStr,
                        noduleCount = countStr,
                        status = statusText,
                        statusColor = statusColor
                    )
                }
                _uiState.update { it.copy(reports = items, isLoading = false, isRefreshing = false, errorMessage = null) }
            } ?: run {
                val err = res.exceptionOrNull()?.message ?: "Failed to fetch reports."
                _uiState.update { it.copy(isLoading = false, isRefreshing = false, errorMessage = err) }
            }
        }
    }

    fun onSearchQueryChange(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
    }

    fun onFilterChange(filter: String) {
        _uiState.update { it.copy(selectedFilter = filter) }
    }

    fun toggleReportSelection(reportId: String) {
        _uiState.update { state ->
            val updatedReports = state.reports.map {
                if (it.id == reportId) it.copy(isSelected = !it.isSelected) else it
            }
            state.copy(reports = updatedReports)
        }
    }

    fun getSelectedReportIds(): List<String> {
        return _uiState.value.reports.filter { it.isSelected }.map { it.id }
    }
}
