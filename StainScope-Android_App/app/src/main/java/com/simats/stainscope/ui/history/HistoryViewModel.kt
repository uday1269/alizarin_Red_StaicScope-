package com.simats.stainscope.ui.history

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

data class HistoryItem(
    val id: String,
    val sampleName: String,
    val date: String,
    val mineralArea: String,
    val stainIntensity: String,
    val noduleCount: String,
    val status: String,
    val isPinned: Boolean = false
)

data class HistoryState(
    val searchQuery: String = "",
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val analyses: List<HistoryItem> = emptyList()
)

class HistoryViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = StainScopeRepository(application)

    private val _uiState = MutableStateFlow(HistoryState())
    val uiState: StateFlow<HistoryState> = _uiState.asStateFlow()

    init {
        loadHistory()
    }

    fun loadHistory(isRefresh: Boolean = false) {
        viewModelScope.launch {
            if (isRefresh) {
                _uiState.update { it.copy(isRefreshing = true) }
            } else {
                _uiState.update { it.copy(isLoading = true) }
            }
            val result = repository.listAnalyses()
            result.getOrNull()?.let { list ->
                val items = list.map { dto ->
                    val areaVal = dto.mineralizedAreaPercent ?: 0.0
                    val areaStr = String.format(Locale.US, "%.2f%%", areaVal)
                    val odVal = dto.opticalDensity ?: dto.opticalDensityProxy ?: 0.0
                    val odStr = String.format(Locale.US, "%.2f OD", odVal)
                    val countStr = dto.noduleCount?.let { String.format(Locale.US, "%,d", it) } ?: "0"
                    val rawDate = dto.analyzedAt ?: dto.createdAt
                    val dateStr = rawDate?.take(10) ?: "Recent"
                    val titleStr = dto.sampleTitle?.ifEmpty { null } ?: "ARS Micrograph (${dto.id.take(8)})"
                    
                    val statusText = when {
                        areaVal >= 40.0 -> "High Mineralization"
                        areaVal >= 15.0 -> "Moderate Mineralization"
                        else -> "Low Mineralization"
                    }

                    HistoryItem(
                        id = dto.id,
                        sampleName = titleStr,
                        date = dateStr,
                        mineralArea = areaStr,
                        stainIntensity = odStr,
                        noduleCount = countStr,
                        status = statusText
                    )
                }
                _uiState.update { it.copy(analyses = items, isLoading = false, isRefreshing = false) }
            } ?: run {
                _uiState.update { it.copy(isLoading = false, isRefreshing = false) }
            }
        }
    }

    fun onSearchQueryChange(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
    }

    fun togglePin(id: String) {
        val newList = _uiState.value.analyses.map {
            if (it.id == id) it.copy(isPinned = !it.isPinned) else it
        }
        _uiState.update { it.copy(analyses = newList) }
    }

    fun deleteAnalysis(id: String) {
        val newList = _uiState.value.analyses.filter { it.id != id }
        _uiState.update { it.copy(analyses = newList) }
        viewModelScope.launch {
            repository.deleteAnalysis(id)
            loadHistory()
        }
    }
}

