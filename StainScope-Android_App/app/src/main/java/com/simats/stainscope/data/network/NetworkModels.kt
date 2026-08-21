package com.simats.stainscope.data.network

import com.google.gson.annotations.SerializedName

// FastAPI Auth DTOs
data class AuthRequest(
    val email: String,
    val password: String,
    @SerializedName("full_name") val fullName: String? = null
)

data class AuthResponse(
    val status: String? = "success",
    @SerializedName("user_id") val userId: String? = null,
    val email: String? = null,
    @SerializedName("full_name") val fullName: String? = null,
    @SerializedName("access_token") val accessToken: String? = null,
    @SerializedName("token_type") val tokenType: String? = null,
    val detail: String? = null
)

data class UserSignUpRequest(
    val email: String,
    val password: String,
    @SerializedName("full_name") val fullName: String? = null
)

data class SignUpResponse(
    val status: String?,
    @SerializedName("user_id") val userId: String?,
    val email: String?,
    val detail: String? = null
)

// User Profile DTOs
data class ProfileDto(
    val id: String? = null,
    @SerializedName("full_name") val fullName: String? = null,
    val role: String? = null,
    val institution: String? = null,
    @SerializedName("lab_name") val labName: String? = null,
    @SerializedName("total_scans") val totalScans: Int? = null
)

data class ProfileUpdateRequest(
    @SerializedName("full_name") val fullName: String? = null,
    val role: String? = null,
    val institution: String? = null,
    @SerializedName("lab_name") val labName: String? = null
)

// Analysis DTOs
data class AnalysisResponseDto(
    @SerializedName("is_valid") val valid: Any? = null,
    val reason: String? = null,
    @SerializedName("analysis_id") val analysisId: String? = null,
    val id: String? = null,
    @SerializedName("micrograph_id") val micrographId: String? = null,
    @SerializedName("user_id") val userId: String? = null,
    @SerializedName("analyzed_at") val analyzedAt: String? = null,
    @SerializedName("created_at") val createdAt: String? = null,
    @SerializedName("sample_title") val sampleTitle: String? = null,
    @SerializedName("cell_line") val cellLine: String? = null,
    @SerializedName("treatment") val treatment: String? = null,
    @SerializedName("differentiation_day") val differentiationDay: String? = null,
    @SerializedName("mineralized_area_percent") val mineralizedAreaPercent: Double? = null,
    @SerializedName("optical_density") val opticalDensity: Double? = null,
    @SerializedName("optical_density_proxy") val opticalDensityProxy: Double? = null,
    @SerializedName("nodule_count") val noduleCount: Int? = null,
    @SerializedName("calcium_density_ug_cm2") val calciumDensityUgCm2: Double? = null,
    @SerializedName("ai_confidence") val aiConfidence: Double? = null,
    @SerializedName("overall_confidence") val overallConfidence: Double? = null,
    @SerializedName("processing_time_sec") val processingTimeSec: Double? = null,
    @SerializedName("objective_magnification") val objectiveMagnification: String? = null,
    @SerializedName("spatial_pattern") val spatialPattern: String? = null,
    @SerializedName("min_nodule_size_pixels") val minNoduleSizePixels: Double? = null,
    @SerializedName("max_nodule_size_pixels") val maxNoduleSizePixels: Double? = null,
    @SerializedName("mean_nodule_size_pixels") val meanNoduleSizePixels: Double? = null,
    @SerializedName("median_nodule_size_pixels") val medianNoduleSizePixels: Double? = null,
    @SerializedName("nodule_size_distribution") val noduleSizeDistribution: Map<String, Any>? = null,
    @SerializedName("quality_warnings") val qualityWarnings: Any? = null,
    val stain: Map<String, Any>? = null,
    @SerializedName("image_quality") val imageQuality: Map<String, Any>? = null,
    val mineralization: MineralizationDto? = null,
    val nodules: NodulesDto? = null,
    val pattern: Map<String, Any>? = null,
    val intensity: Map<String, Any>? = null,
    val quality: Map<String, Any>? = null,
    val calibration: Map<String, Any>? = null,
    @SerializedName("physical_metrics") val physicalMetrics: Map<String, Any>? = null,
    val overlay: String? = null,
    val overlays: Any? = null,
    @SerializedName("image_url") val imageUrl: String? = null
) {
    val isValid: Boolean
        get() = when (valid) {
            is Boolean -> valid
            is Number -> valid.toInt() == 1
            is String -> valid.equals("true", ignoreCase = true) || valid == "1"
            else -> true
        }
}

data class MineralizationDto(
    val area: Double? = null,
    @SerializedName("area_pixels") val areaPixels: Long? = null,
    @SerializedName("area_percent") val areaPercent: Double? = null,
    @SerializedName("total_area") val totalArea: Long? = null,
    @SerializedName("total_pixels") val totalPixels: Long? = null,
    @SerializedName("density_per_10k_px") val densityPer10kPx: Double? = null,
    @SerializedName("spatial_pattern") val spatialPattern: Map<String, Any>? = null,
    @SerializedName("optical_density") val opticalDensity: Double? = null
)

data class NodulesDto(
    val count: Int? = null,
    val min: Double? = null,
    val max: Double? = null,
    val mean: Double? = null,
    val median: Double? = null,
    @SerializedName("min_size_pixels") val minSizePixels: Double? = null,
    @SerializedName("max_size_pixels") val maxSizePixels: Double? = null,
    @SerializedName("mean_size_pixels") val meanSizePixels: Double? = null,
    @SerializedName("median_size_pixels") val medianSizePixels: Double? = null,
    @SerializedName("size_distribution") val sizeDistribution: Map<String, Any>? = null
)

data class OverlaysDto(
    @SerializedName("nodule_map") val noduleMap: String? = null,
    val overlay: String? = null,
    val mask: String? = null,
    @SerializedName("validation_panel") val validationPanel: String? = null
)

data class AnalysisSummaryDto(
    val id: String,
    @SerializedName("micrograph_id") val micrographId: String? = null,
    @SerializedName("sample_title") val sampleTitle: String? = null,
    @SerializedName("analyzed_at") val analyzedAt: String? = null,
    @SerializedName("created_at") val createdAt: String? = null,
    @SerializedName("mineralized_area_percent") val mineralizedAreaPercent: Double? = null,
    @SerializedName("nodule_count") val noduleCount: Int? = null,
    @SerializedName("optical_density") val opticalDensity: Double? = null,
    @SerializedName("optical_density_proxy") val opticalDensityProxy: Double? = null,
    @SerializedName("calcium_density_ug_cm2") val calciumDensityUgCm2: Double? = null,
    @SerializedName("ai_confidence") val aiConfidence: Double? = null,
    @SerializedName("overall_confidence") val overallConfidence: Double? = null,
    val status: String? = null,
    @SerializedName("user_id") val userId: String? = null,
    @SerializedName("image_url") val imageUrl: String? = null,
    val overlay: String? = null,
    val overlays: Any? = null
)

// Research Note DTOs
data class ResearchNoteCreateRequest(
    val title: String,
    val content: String
)

data class ResearchNoteDto(
    val id: String,
    val title: String,
    val content: String,
    @SerializedName("created_at") val createdAt: String? = null,
    @SerializedName("user_id") val userId: String? = null
)

// Comparison DTOs
data class ComparisonSaveRequest(
    val title: String,
    @SerializedName("analysis_ids") val analysisIds: List<String>,
    @SerializedName("ranking_summary") val rankingSummary: Map<String, Any>? = null
)

data class ComparisonDto(
    val id: String,
    val title: String,
    @SerializedName("analysis_ids") val analysisIds: List<String>? = null,
    @SerializedName("ranking_summary") val rankingSummary: Map<String, Any>? = null,
    @SerializedName("created_at") val createdAt: String? = null,
    @SerializedName("user_id") val userId: String? = null
)
