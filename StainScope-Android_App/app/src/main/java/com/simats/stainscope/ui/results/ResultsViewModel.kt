package com.simats.stainscope.ui.results

import android.app.Application
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.simats.stainscope.data.repository.StainScopeRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.Locale

enum class InspectionMode {
    Original, Segmentation, Heatmap
}

data class SpectralItem(
    val name: String,
    val percentage: Double,
    val color: Color
)

data class ResultsState(
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val errorMessage: String? = null,
    val sampleId: String = "",
    val sampleName: String = "ARS Microscopy Sample",
    val analysisDate: String = "",
    val magnification: String = "20x Objective",
    val mineralizedAreaFraction: String = "0.00%",
    val areaDensityLabel: String = "Mineralized Surface Area",
    val stainIntensity: String = "0.00 OD",
    val absorbanceLabel: String = "Stain Intensity Proxy",
    val calcifiedNodules: String = "0",
    val noduleLabel: String = "Calcified Nodules Count",
    val estimatedCalcium: String = "0.00 μg/cm²",
    val calciumLabel: String = "Calcium Density",
    val aiConfidence: String = "0.0%",
    val runtime: String = "0.00s",
    val minNoduleSize: String = "0.00 px",
    val maxNoduleSize: String = "0.00 px",
    val meanNoduleSize: String = "0.00 px",
    val medianNoduleSize: String = "0.00 px",
    val dotCount: String = "0",
    val smallCount: String = "0",
    val mediumCount: String = "0",
    val largeCount: String = "0",
    val plaqueCount: String = "0",
    val spatialPattern: String = "N/A",
    val warnings: List<String> = emptyList(),
    val imageUrl: String? = null,
    val overlayUrl: String? = null,
    val heatmapUrl: String? = null,
    val inspectionMode: InspectionMode = InspectionMode.Segmentation,
    val spectralBreakdown: List<SpectralItem> = listOf(
        SpectralItem("Deep Red (Dense Calcification)", 38.5, Color(0xFF8B1D1D)),
        SpectralItem("Crimson (Moderate Nodule)", 26.2, Color(0xFFB71C1C)),
        SpectralItem("Light Pink (Diffused Stain)", 19.8, Color(0xFFEF9A9A)),
        SpectralItem("Unstained Matrix / Background", 15.5, Color(0xFFF5F5F5))
    ),
    val scientificNotes: String = "Classical CV mineralization quantification engine result."
) {
    val currentDisplayImageUrl: String?
        get() = when (inspectionMode) {
            InspectionMode.Original -> imageUrl ?: overlayUrl
            InspectionMode.Segmentation -> overlayUrl ?: imageUrl
            InspectionMode.Heatmap -> heatmapUrl ?: overlayUrl ?: imageUrl
        }
}

class ResultsViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = StainScopeRepository(application)
    private val _uiState = MutableStateFlow(ResultsState())
    val uiState: StateFlow<ResultsState> = _uiState.asStateFlow()
    private var currentAnalysisId: String = ""

    fun loadAnalysisDetail(sampleId: String, isRefresh: Boolean = false) {
        if (sampleId.isEmpty()) return
        currentAnalysisId = sampleId

        if (isRefresh) {
            _uiState.value = _uiState.value.copy(isRefreshing = true, errorMessage = null)
        } else {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
        }

        viewModelScope.launch {
            val res = repository.getAnalysisDetail(sampleId)
            res.getOrNull()?.let { dto ->
                val idVal = dto.id ?: dto.analysisId ?: sampleId
                val areaNum = dto.mineralization?.areaPercent ?: dto.mineralizedAreaPercent ?: 0.0
                val areaFraction = String.format(Locale.US, "%.2f%%", areaNum)

                val odNum = dto.mineralization?.opticalDensity ?: dto.opticalDensity ?: dto.opticalDensityProxy ?: 0.0
                val od = String.format(Locale.US, "%.2f OD", odNum)

                val countNum = dto.nodules?.count ?: dto.noduleCount ?: 0
                val count = String.format(Locale.US, "%,d", countNum)

                val calciumNum = dto.calciumDensityUgCm2 ?: (areaNum * 0.05)
                val calciumStr = String.format(Locale.US, "%.2f μg/cm²", calciumNum)

                val title = dto.sampleTitle?.ifEmpty { null } ?: "ARS Microscopy Sample"
                val rawDate = dto.analyzedAt ?: dto.createdAt
                val date = rawDate?.take(16)?.replace("T", " at ") ?: ""

                val confidenceVal = dto.calibration?.get("ai_confidence") as? Double
                    ?: dto.aiConfidence 
                    ?: dto.overallConfidence 
                    ?: 0.95
                val confidencePct = if (confidenceVal <= 1.0) confidenceVal * 100.0 else confidenceVal
                val confidenceStr = String.format(Locale.US, "%.1f%%", confidencePct)

                val timeSec = dto.processingTimeSec ?: 0.45
                val runtimeStr = String.format(Locale.US, "%.2fs", timeSec)

                val minSize = dto.nodules?.minSizePixels ?: dto.minNoduleSizePixels ?: dto.nodules?.min ?: 0.0
                val maxSize = dto.nodules?.maxSizePixels ?: dto.maxNoduleSizePixels ?: dto.nodules?.max ?: 0.0
                val meanSize = dto.nodules?.meanSizePixels ?: dto.meanNoduleSizePixels ?: dto.nodules?.mean ?: 0.0
                val medianSize = dto.nodules?.medianSizePixels ?: dto.medianNoduleSizePixels ?: dto.nodules?.median ?: 0.0

                val dist = dto.nodules?.sizeDistribution ?: dto.noduleSizeDistribution ?: emptyMap()
                val dot = dist["dot"]?.toString() ?: dist["Dot"]?.toString() ?: "0"
                val small = dist["small"]?.toString() ?: dist["Small"]?.toString() ?: "0"
                val medium = dist["medium"]?.toString() ?: dist["Medium"]?.toString() ?: "0"
                val large = dist["large"]?.toString() ?: dist["Large"]?.toString() ?: "0"
                val plaque = dist["plaque"]?.toString() ?: dist["Plaque"]?.toString() ?: "0"

                val spatial = dto.spatialPattern
                    ?: dto.mineralization?.spatialPattern?.get("type")?.toString() 
                    ?: dto.mineralization?.spatialPattern?.get("pattern")?.toString()
                    ?: dto.pattern?.get("spatial_mineralization_pattern")?.toString()
                    ?: "N/A"

                val mag = dto.objectiveMagnification ?: "20x Objective"
                val warningsList = when (val w = dto.qualityWarnings) {
                    is List<*> -> w.mapNotNull { it?.toString() }
                    is String -> if (w.isNotBlank() && w != "[]") listOf(w) else emptyList()
                    else -> emptyList()
                }

                val overlaysMap = (dto.overlays as? Map<*, *>)
                val rawImg = repository.resolveImageUrl(dto.imageUrl)
                val segmentationImg = repository.resolveImageUrl(
                    dto.overlay ?: overlaysMap?.get("nodule_map")?.toString() ?: overlaysMap?.get("contour_map")?.toString() ?: rawImg
                )
                val heatmapImg = repository.resolveImageUrl(
                    overlaysMap?.get("overlay")?.toString() ?: overlaysMap?.get("heatmap")?.toString() ?: overlaysMap?.get("mask")?.toString() ?: segmentationImg
                )

                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    isRefreshing = false,
                    errorMessage = null,
                    sampleId = idVal,
                    sampleName = title,
                    analysisDate = date,
                    magnification = mag,
                    mineralizedAreaFraction = areaFraction,
                    stainIntensity = od,
                    calcifiedNodules = count,
                    estimatedCalcium = calciumStr,
                    aiConfidence = confidenceStr,
                    runtime = runtimeStr,
                    minNoduleSize = String.format(Locale.US, "%.2f px", minSize),
                    maxNoduleSize = String.format(Locale.US, "%.2f px", maxSize),
                    meanNoduleSize = String.format(Locale.US, "%.2f px", meanSize),
                    medianNoduleSize = String.format(Locale.US, "%.2f px", medianSize),
                    dotCount = dot,
                    smallCount = small,
                    mediumCount = medium,
                    largeCount = large,
                    plaqueCount = plaque,
                    spatialPattern = spatial,
                    warnings = warningsList,
                    imageUrl = rawImg,
                    overlayUrl = segmentationImg ?: rawImg,
                    heatmapUrl = heatmapImg ?: segmentationImg ?: rawImg,
                    scientificNotes = "Classical CV mineralization quantification engine result. Sample: $title (ID: $idVal)"
                )
            } ?: run {
                val err = res.exceptionOrNull()?.message ?: "Analysis details failed to load."
                _uiState.value = _uiState.value.copy(isLoading = false, isRefreshing = false, errorMessage = err)
            }
        }
    }

    fun refresh() {
        if (currentAnalysisId.isNotEmpty()) {
            loadAnalysisDetail(currentAnalysisId, isRefresh = true)
        } else {
            _uiState.value = _uiState.value.copy(isRefreshing = false)
        }
    }

    fun setInspectionMode(mode: InspectionMode) {
        _uiState.value = _uiState.value.copy(inspectionMode = mode)
    }
}
