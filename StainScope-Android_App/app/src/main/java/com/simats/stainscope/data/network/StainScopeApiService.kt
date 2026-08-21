package com.simats.stainscope.data.network

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

interface StainScopeApiService {

    // User Profile
    @GET("profile")
    suspend fun getProfile(
        @Header("Authorization") token: String
    ): Response<ProfileDto>

    @PUT("profile")
    suspend fun updateProfile(
        @Header("Authorization") token: String,
        @Body request: ProfileUpdateRequest
    ): Response<ProfileDto>

    // Image Upload & Analysis Run
    @Multipart
    @POST("analyze")
    suspend fun analyzeImage(
        @Header("Authorization") token: String,
        @Part file: MultipartBody.Part,
        @Part("pixel_size_um") pixelSizeUm: RequestBody? = null,
        @Part("sample_title") sampleTitle: RequestBody? = null,
        @Part("cell_line") cellLine: RequestBody? = null,
        @Part("treatment") treatment: RequestBody? = null,
        @Part("differentiation_day") differentiationDay: RequestBody? = null
    ): Response<AnalysisResponseDto>

    // Analysis History & Details
    @GET("analyses")
    suspend fun listAnalyses(
        @Header("Authorization") token: String
    ): Response<List<AnalysisSummaryDto>>

    @GET("analyses/{analysis_id}")
    suspend fun getAnalysisDetail(
        @Path("analysis_id") analysisId: String,
        @Header("Authorization") token: String
    ): Response<AnalysisResponseDto>

    @DELETE("analyses/{analysis_id}")
    suspend fun deleteAnalysis(
        @Path("analysis_id") analysisId: String,
        @Header("Authorization") token: String
    ): Response<Map<String, Any>>

    @GET("analyses/deleted")
    suspend fun listDeletedAnalyses(
        @Header("Authorization") token: String
    ): Response<List<AnalysisSummaryDto>>

    @POST("analyses/{analysis_id}/restore")
    suspend fun restoreAnalysis(
        @Path("analysis_id") analysisId: String,
        @Header("Authorization") token: String
    ): Response<Map<String, Any>>

    // Research Notes
    @GET("notes")
    suspend fun listNotes(
        @Header("Authorization") token: String
    ): Response<List<ResearchNoteDto>>

    @POST("notes")
    suspend fun createNote(
        @Header("Authorization") token: String,
        @Body request: ResearchNoteCreateRequest
    ): Response<ResearchNoteDto>

    @DELETE("notes/{note_id}")
    suspend fun deleteNote(
        @Path("note_id") noteId: String,
        @Header("Authorization") token: String
    ): Response<Map<String, Any>>

    @GET("notes/deleted")
    suspend fun listDeletedNotes(
        @Header("Authorization") token: String
    ): Response<List<ResearchNoteDto>>

    @POST("notes/{note_id}/restore")
    suspend fun restoreNote(
        @Path("note_id") noteId: String,
        @Header("Authorization") token: String
    ): Response<Map<String, Any>>

    // Saved Comparisons
    @GET("saved-comparisons")
    suspend fun listSavedComparisons(
        @Header("Authorization") token: String
    ): Response<List<ComparisonDto>>

    @POST("saved-comparisons")
    suspend fun createSavedComparison(
        @Header("Authorization") token: String,
        @Body request: ComparisonSaveRequest
    ): Response<ComparisonDto>

    @DELETE("saved-comparisons/{comp_id}")
    suspend fun deleteSavedComparison(
        @Path("comp_id") compId: String,
        @Header("Authorization") token: String
    ): Response<Map<String, Any>>
}
