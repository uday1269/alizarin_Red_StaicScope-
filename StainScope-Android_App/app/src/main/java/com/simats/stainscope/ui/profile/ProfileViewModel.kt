package com.simats.stainscope.ui.profile

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.simats.stainscope.data.repository.StainScopeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.UUID

import java.util.Locale

data class Note(
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val date: String,
    val content: String
)

data class PinnedResult(
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val subtitle: String,
    val sampleId: String
)

data class DeletedItem(
    val id: String = UUID.randomUUID().toString(),
    val type: String, // "Note" or "Result"
    val title: String,
    val note: Note? = null,
    val pinnedResult: PinnedResult? = null,
    val deletedAt: Long = System.currentTimeMillis()
)

data class ProfileState(
    val name: String = "Dr. Researcher",
    val title: String = "Senior Bone Tissue Engineer",
    val email: String = "user@stainscope.org",
    val institution: String = "BioMed Research Institute",
    val laboratory: String = "Regenerative Medicine & Osteogenesis Lab",
    val totalScans: Int = 0,
    val isDarkMode: Boolean = false,
    val notes: List<Note> = emptyList(),
    val pinnedResults: List<PinnedResult> = emptyList(),
    val exportFormat: String = "Scientific PDF (Charts + Vector)",
    val overlayOriginal: Boolean = true,
    val aiContourMap: Boolean = true,
    val recycleBin: List<DeletedItem> = emptyList(),
    val isEditingProfile: Boolean = false,
    val isRefreshing: Boolean = false
)

class ProfileViewModel(application: Application) : AndroidViewModel(application) {
    private val prefs = application.getSharedPreferences("stainscope_prefs", Context.MODE_PRIVATE)
    private val repository = StainScopeRepository(application)
    
    private val _uiState = MutableStateFlow(ProfileState(
        isDarkMode = prefs.getBoolean("dark_mode", false),
        email = repository.getSessionManager().getUserEmail() ?: "user@stainscope.org"
    ))
    val uiState: StateFlow<ProfileState> = _uiState.asStateFlow()

    init {
        loadProfileAndNotes()
    }

    fun loadProfileAndNotes(isRefresh: Boolean = false) {
        if (isRefresh) {
            _uiState.update { it.copy(isRefreshing = true) }
        }
        viewModelScope.launch {
            // Load Profile
            val profileRes = repository.getProfile()
            profileRes.getOrNull()?.let { profile ->
                _uiState.update { state ->
                    state.copy(
                        name = profile.fullName ?: state.name,
                        title = profile.role ?: state.title,
                        email = repository.getSessionManager().getUserEmail() ?: state.email,
                        institution = profile.institution ?: state.institution,
                        laboratory = profile.labName ?: state.laboratory,
                        totalScans = profile.totalScans ?: state.totalScans
                    )
                }
            }

            // Load Research Notes
            val notesRes = repository.listNotes()
            notesRes.getOrNull()?.let { noteDtos ->
                val mappedNotes = noteDtos.map { dto ->
                    val dateStr = dto.createdAt?.take(10) ?: "AUG 07, 2026"
                    Note(
                        id = dto.id,
                        title = dto.title,
                        date = dateStr,
                        content = dto.content
                    )
                }
                _uiState.update { it.copy(notes = mappedNotes) }
            }

            // Load User Analyses for Pinned Results
            val analysesRes = repository.listAnalyses()
            analysesRes.getOrNull()?.let { list ->
                val pinned = list.take(3).map { item ->
                    val areaStr = if (item.mineralizedAreaPercent != null) String.format(Locale.US, "%.2f%%", item.mineralizedAreaPercent) else "0.00%"
                    PinnedResult(
                        id = item.id,
                        title = item.sampleTitle ?: "ARS Microscopy Sample",
                        subtitle = "ID: ${item.id.take(8)} • Area: $areaStr",
                        sampleId = item.id
                    )
                }
                _uiState.update { it.copy(pinnedResults = pinned, totalScans = list.size, isRefreshing = false) }
            } ?: run {
                _uiState.update { it.copy(isRefreshing = false) }
            }

            // Load Deleted Items for Recycle Bin
            val deletedAnalysesRes = repository.listDeletedAnalyses()
            val deletedNotesRes = repository.listDeletedNotes()
            val deletedItemsList = mutableListOf<DeletedItem>()

            deletedAnalysesRes.getOrNull()?.forEach { dto ->
                deletedItemsList.add(
                    DeletedItem(
                        id = dto.id,
                        type = "Result",
                        title = dto.sampleTitle ?: "ARS Microscopy Sample (${dto.id.take(8)})"
                    )
                )
            }

            deletedNotesRes.getOrNull()?.forEach { noteDto ->
                deletedItemsList.add(
                    DeletedItem(
                        id = noteDto.id,
                        type = "Note",
                        title = noteDto.title
                    )
                )
            }

            _uiState.update { it.copy(recycleBin = deletedItemsList) }
        }
    }

    fun onToggleDarkMode(enabled: Boolean) {
        prefs.edit().putBoolean("dark_mode", enabled).apply()
        _uiState.update { it.copy(isDarkMode = enabled) }
    }

    fun setEditingProfile(editing: Boolean) {
        _uiState.update { it.copy(isEditingProfile = editing) }
    }

    fun updateProfile(name: String, title: String, institution: String, lab: String) {
        _uiState.update { it.copy(
            name = name,
            title = title,
            institution = institution,
            laboratory = lab,
            isEditingProfile = false
        ) }
        viewModelScope.launch {
            repository.updateProfile(fullName = name, role = title, institution = institution, labName = lab)
        }
    }

    fun addNote(title: String, content: String) {
        viewModelScope.launch {
            val res = repository.createNote(title, content)
            res.getOrNull()?.let { dto ->
                val newNote = Note(
                    id = dto.id,
                    title = dto.title,
                    date = dto.createdAt?.take(10) ?: "OCT 24, 2026",
                    content = dto.content
                )
                _uiState.update { it.copy(notes = it.notes + newNote) }
            } ?: run {
                val newNote = Note(title = title, date = "OCT 24, 2026", content = content)
                _uiState.update { it.copy(notes = it.notes + newNote) }
            }
        }
    }

    fun deleteNote(noteId: String) {
        val note = _uiState.value.notes.find { it.id == noteId }
        if (note != null) {
            val deletedItem = DeletedItem(type = "Note", title = note.title, note = note)
            _uiState.update { it.copy(
                notes = it.notes.filter { n -> n.id != noteId },
                recycleBin = it.recycleBin + deletedItem
            ) }
            viewModelScope.launch {
                repository.deleteNote(noteId)
                loadProfileAndNotes()
            }
        }
    }

    fun signOut() {
        repository.signOut()
    }

    fun deletePinnedResult(resultId: String) {
        val result = _uiState.value.pinnedResults.find { it.id == resultId }
        if (result != null) {
            val deletedItem = DeletedItem(type = "Result", title = result.title, pinnedResult = result)
            _uiState.update { it.copy(
                pinnedResults = it.pinnedResults.filter { r -> r.id != resultId },
                recycleBin = it.recycleBin + deletedItem
            ) }
            viewModelScope.launch {
                repository.deleteAnalysis(resultId)
                loadProfileAndNotes()
            }
        }
    }

    fun restoreItem(itemId: String) {
        val item = _uiState.value.recycleBin.find { it.id == itemId }
        _uiState.update { state ->
            state.copy(recycleBin = state.recycleBin.filter { it.id != itemId })
        }
        viewModelScope.launch {
            if (item?.type == "Note") {
                repository.restoreNote(itemId)
            } else {
                repository.restoreAnalysis(itemId)
            }
            loadProfileAndNotes()
        }
    }

    fun permanentlyDeleteItem(itemId: String) {
        _uiState.update { it.copy(
            recycleBin = it.recycleBin.filter { item -> item.id != itemId }
        ) }
    }

    fun clearRecycleBin() {
        _uiState.update { it.copy(recycleBin = emptyList()) }
    }

    fun updateExportFormat(format: String) {
        _uiState.update { it.copy(exportFormat = format) }
    }

    fun toggleOverlayOriginal(value: Boolean) {
        _uiState.update { it.copy(overlayOriginal = value) }
    }

    fun toggleAiContourMap(value: Boolean) {
        _uiState.update { it.copy(aiContourMap = value) }
    }

    fun clearOldRecycleBinItems() {
        val twentyEightDaysInMillis = 28L * 24 * 60 * 60 * 1000
        val currentTime = System.currentTimeMillis()
        _uiState.update { state ->
            state.copy(recycleBin = state.recycleBin.filter { 
                currentTime - it.deletedAt < twentyEightDaysInMillis 
            })
        }
    }
}
