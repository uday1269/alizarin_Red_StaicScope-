package com.simats.stainscope.ui.dashboard

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.simats.stainscope.data.repository.StainScopeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

import java.util.Locale

data class DashboardState(
    val userName: String = "Dr. Researcher",
    val labName: String = "Regenerative Medicine & Osteogenesis Lab",
    val totalScans: Int = 0,
    val avgAreaPercentStr: String = "0.00%",
    val highCalcifiedCount: Int = 0,
    val aiAccuracyStr: String = "0.0%",
    val aiLatency: String = "38 ms",
    val engineConfidence: String = "99.4%",
    val engineUptime: String = "99.9%",
    val recentScans: List<StainScan> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false
)

data class StainScan(
    val id: String = "STAIN-8092",
    val sampleInfo: String,
    val date: String,
    val mineralizationArea: String
)

class DashboardViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = StainScopeRepository(application)

    private val _uiState = MutableStateFlow(DashboardState())
    val uiState: StateFlow<DashboardState> = _uiState.asStateFlow()

    init {
        loadDashboardData()
    }

    fun loadDashboardData(isRefresh: Boolean = false) {
        viewModelScope.launch {
            if (isRefresh) {
                _uiState.update { it.copy(isRefreshing = true) }
            } else {
                _uiState.update { it.copy(isLoading = true) }
            }

            // 1. Fetch User Profile
            val profileRes = repository.getProfile()
            var currentName = _uiState.value.userName
            var currentLab = _uiState.value.labName

            profileRes.getOrNull()?.let { profile ->
                if (!profile.fullName.isNullOrEmpty()) currentName = profile.fullName
                if (!profile.labName.isNullOrEmpty()) currentLab = profile.labName
            }

            // 2. Fetch User Analyses History
            val analysesRes = repository.listAnalyses()
            var scansCount = 0
            var avgArea = 0.0
            var highCalcCount = 0
            var avgConfidence = 0.0
            val scansList = mutableListOf<StainScan>()

            analysesRes.getOrNull()?.let { list ->
                scansCount = list.size
                if (list.isNotEmpty()) {
                    val totalAreaSum = list.sumOf { it.mineralizedAreaPercent ?: 0.0 }
                    avgArea = totalAreaSum / list.size
                    highCalcCount = list.count { (it.mineralizedAreaPercent ?: 0.0) >= 20.0 }
                    val totalConfSum = list.sumOf { it.overallConfidence ?: it.aiConfidence ?: 0.98 }
                    avgConfidence = totalConfSum / list.size
                }

                list.take(5).forEach { item ->
                    val title = item.sampleTitle?.ifEmpty { null } ?: "ARS Micrograph (${item.id.take(8)})"
                    val rawDate = item.analyzedAt ?: item.createdAt
                    val dateStr = rawDate?.take(16)?.replace("T", " ") ?: "Recent"
                    val areaStr = if (item.mineralizedAreaPercent != null) {
                        String.format(Locale.US, "%.2f%%", item.mineralizedAreaPercent)
                    } else {
                        "0.00%"
                    }
                    scansList.add(StainScan(item.id, title, dateStr, areaStr))
                }
            }

            val confFormatted = if (scansCount > 0) {
                String.format(Locale.US, "%.1f%%", if (avgConfidence <= 1.0) avgConfidence * 100 else avgConfidence)
            } else {
                "0.0%"
            }
            val avgAreaFormatted = if (scansCount > 0) String.format(Locale.US, "%.2f%%", avgArea) else "0.00%"

            _uiState.update {
                it.copy(
                    userName = currentName,
                    labName = currentLab,
                    totalScans = scansCount,
                    avgAreaPercentStr = avgAreaFormatted,
                    highCalcifiedCount = highCalcCount,
                    aiAccuracyStr = confFormatted,
                    engineConfidence = confFormatted.ifBlank { "99.4%" },
                    recentScans = scansList,
                    isLoading = false,
                    isRefreshing = false
                )
            }
        }
    }
}
