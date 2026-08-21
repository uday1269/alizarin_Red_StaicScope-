package com.simats.stainscope.data.repository

import android.content.Context
import com.simats.stainscope.data.SessionManager
import com.simats.stainscope.data.local.*
import com.simats.stainscope.data.network.*
import kotlinx.coroutines.flow.Flow
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.*

class StainScopeRepository(context: Context) {

    private val sessionManager = SessionManager(context.applicationContext)
    private val fastApiAuthService = ApiClient.fastApiAuthService
    private val apiService = ApiClient.fastApiService
    private val database = StainScopeDatabase.getDatabase(context)
    private val analysisDao = database.analysisDao()

    fun isLoggedIn(): Boolean = sessionManager.isLoggedIn()

    fun getSessionManager(): SessionManager = sessionManager

    fun getBearerToken(): String? {
        val token = sessionManager.getAccessToken() ?: return null
        return "Bearer $token"
    }

    suspend fun signIn(email: String, password: String): Result<AuthResponse> {
        return try {
            val response = fastApiAuthService.login(AuthRequest(email = email.trim(), password = password))
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                val accessToken = body.accessToken
                val userId = body.userId
                if (!accessToken.isNullOrEmpty() && !userId.isNullOrEmpty()) {
                    sessionManager.saveSession(
                        accessToken = accessToken,
                        refreshToken = "",
                        userId = userId,
                        email = body.email ?: email,
                        fullName = body.fullName ?: email.substringBefore("@")
                    )
                    Result.success(body)
                } else {
                    Result.failure(Exception("Invalid authentication response format."))
                }
            } else {
                val errorBody = response.errorBody()?.string()
                val msg = parseErrorMessage(errorBody, "Invalid email or password.")
                Result.failure(Exception(msg))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun signUp(email: String, password: String, fullName: String): Result<Boolean> {
        val trimmedEmail = email.trim()
        val displayName = fullName.ifEmpty { trimmedEmail.substringBefore("@") }

        return try {
            val req = AuthRequest(email = trimmedEmail, password = password, fullName = displayName)
            val response = fastApiAuthService.signup(req)
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                val accessToken = body.accessToken
                val userId = body.userId
                if (!accessToken.isNullOrEmpty() && !userId.isNullOrEmpty()) {
                    sessionManager.saveSession(
                        accessToken = accessToken,
                        refreshToken = "",
                        userId = userId,
                        email = body.email ?: trimmedEmail,
                        fullName = body.fullName ?: displayName
                    )
                    Result.success(true)
                } else {
                    // Try to sign in if user was created
                    signIn(trimmedEmail, password).map { true }
                }
            } else {
                val errorBody = response.errorBody()?.string()
                val msg = parseErrorMessage(errorBody, "Sign up failed.")
                Result.failure(Exception(msg))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun signOut() {
        sessionManager.clearSession()
    }

    suspend fun getProfile(): Result<ProfileDto> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.getProfile(token)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val err = parseErrorMessage(response.errorBody()?.string(), "Failed to load user profile.")
                Result.failure(Exception(err))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateProfile(fullName: String?, role: String?, institution: String?, labName: String?): Result<ProfileDto> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        val userId = sessionManager.getUserId()
        val req = ProfileUpdateRequest(fullName, role, institution, labName)

        return try {
            val response = apiService.updateProfile(token, req)
            if (response.isSuccessful && response.body() != null) {
                val updated = response.body()!!
                if (!fullName.isNullOrEmpty()) {
                    sessionManager.saveSession(
                        accessToken = sessionManager.getAccessToken() ?: "",
                        refreshToken = sessionManager.getRefreshToken() ?: "",
                        userId = userId ?: "",
                        email = sessionManager.getUserEmail() ?: "",
                        fullName = fullName
                    )
                }
                Result.success(updated)
            } else {
                val err = parseErrorMessage(response.errorBody()?.string(), "Failed to update profile.")
                Result.failure(Exception(err))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun analyzeImage(
        imageBytes: ByteArray,
        fileName: String = "micrograph.png",
        mimeType: String = "image/png",
        sampleTitle: String? = null,
        pixelSizeUm: Float? = null,
        cellLine: String? = null,
        treatment: String? = null
    ): Result<AnalysisResponseDto> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        
        // Save experiment metadata locally first
        val experimentId = UUID.randomUUID().toString()
        val metadataParts = treatment?.split(" | ")
        val incubation = metadataParts?.getOrNull(0) ?: "N/A"
        val magnification = metadataParts?.getOrNull(1) ?: "N/A"
        
        val experiment = ExperimentEntity(
            id = experimentId,
            name = sampleTitle ?: fileName,
            cellLine = cellLine ?: "Unknown",
            incubationPeriod = incubation,
            magnification = magnification
        )
        analysisDao.insertExperiment(experiment)

        return try {
            val requestFile = imageBytes.toRequestBody(mimeType.toMediaTypeOrNull())
            val bodyPart = MultipartBody.Part.createFormData("file", fileName, requestFile)

            val titlePart = sampleTitle?.toRequestBody("text/plain".toMediaTypeOrNull())
            val pixelPart = pixelSizeUm?.toString()?.toRequestBody("text/plain".toMediaTypeOrNull())
            val cellPart = cellLine?.toRequestBody("text/plain".toMediaTypeOrNull())
            val treatPart = treatment?.toRequestBody("text/plain".toMediaTypeOrNull())

            val response = apiService.analyzeImage(
                token = token,
                file = bodyPart,
                pixelSizeUm = pixelPart,
                sampleTitle = titlePart,
                cellLine = cellPart,
                treatment = treatPart
            )

            if (response.isSuccessful && response.body() != null) {
                val resDto = response.body()!!
                if (resDto.isValid) {
                    // Save result to local database
                    val resultEntity = AnalysisResultEntity(
                        analysisId = resDto.id ?: resDto.analysisId ?: UUID.randomUUID().toString(),
                        experimentId = experimentId,
                        mineralizedAreaPercent = resDto.mineralizedAreaPercent ?: 0.0,
                        noduleCount = resDto.noduleCount ?: 0,
                        opticalDensity = resDto.opticalDensity ?: 0.0,
                        aiConfidence = resDto.aiConfidence ?: 0.0,
                        imageUrl = resDto.imageUrl,
                        analyzedAt = resDto.analyzedAt
                    )
                    analysisDao.insertAnalysisResult(resultEntity)
                    
                    lastAnalysisResponse = resDto
                    Result.success(resDto)
                } else {
                    Result.failure(Exception(resDto.reason ?: "Image analysis failed."))
                }
            } else {
                val errBody = response.errorBody()?.string()
                val msg = parseErrorMessage(errBody, "Analysis request failed.")
                Result.failure(Exception(msg))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getLocalReports(): Flow<List<ExperimentWithResult>> {
        return analysisDao.getAllExperimentsWithResults()
    }

    fun resolveImageUrl(url: String?): String? {
        if (url.isNullOrEmpty()) return null
        if (url.startsWith("data:")) return url

        var fullUrl = url
        val configuredHost = ApiConfig.FASTAPI_BASE_URL
            .removePrefix("http://")
            .removePrefix("https://")
            .removeSuffix("/")
        if (fullUrl.contains("127.0.0.1:8000")) {
            fullUrl = fullUrl.replace("127.0.0.1:8000", configuredHost)
        } else if (fullUrl.contains("localhost:8000")) {
            fullUrl = fullUrl.replace("localhost:8000", configuredHost)
        }

        if (!fullUrl.startsWith("http://") && !fullUrl.startsWith("https://")) {
            val cleanBase = ApiConfig.FASTAPI_BASE_URL.removeSuffix("/")
            val cleanPath = if (fullUrl.startsWith("/")) fullUrl else "/$fullUrl"
            fullUrl = "$cleanBase$cleanPath"
        }

        val token = sessionManager.getAccessToken()
        if (!token.isNullOrEmpty() && !fullUrl.contains("token=") && !fullUrl.startsWith("data:")) {
            val connector = if (fullUrl.contains("?")) "&" else "?"
            fullUrl = "$fullUrl${connector}token=$token"
        }
        return fullUrl
    }

    suspend fun listAnalyses(): Result<List<AnalysisSummaryDto>> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.listAnalyses(token)
            if (response.isSuccessful && response.body() != null) {
                val list = response.body()!!.map { item ->
                    item.copy(
                        imageUrl = resolveImageUrl(item.imageUrl),
                        overlay = resolveImageUrl(item.overlay)
                    )
                }
                Result.success(list)
            } else {
                val err = parseErrorMessage(response.errorBody()?.string(), "Failed to fetch analysis history.")
                Result.failure(Exception(err))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getAnalysisDetail(analysisId: String): Result<AnalysisResponseDto> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        
        return try {
            val response = apiService.getAnalysisDetail(analysisId, token)
            if (response.isSuccessful && response.body() != null) {
                val rawDto = response.body()!!
                val resolvedDto = rawDto.copy(
                    imageUrl = resolveImageUrl(rawDto.imageUrl),
                    overlay = resolveImageUrl(rawDto.overlay)
                )
                lastAnalysisResponse = resolvedDto
                Result.success(resolvedDto)
            } else {
                val err = parseErrorMessage(response.errorBody()?.string(), "Analysis record not found.")
                Result.failure(Exception(err))
            }
        } catch (e: Exception) {
            android.util.Log.e("StainScopeRepo", "Error fetching analysis detail ($analysisId): ${e.message}", e)
            Result.failure(e)
        }
    }

    companion object {
        var lastAnalysisResponse: AnalysisResponseDto? = null
    }

    suspend fun listNotes(): Result<List<ResearchNoteDto>> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.listNotes(token)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val err = parseErrorMessage(response.errorBody()?.string(), "Failed to fetch research notes.")
                Result.failure(Exception(err))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createNote(title: String, content: String): Result<ResearchNoteDto> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.createNote(token, ResearchNoteCreateRequest(title, content))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val err = parseErrorMessage(response.errorBody()?.string(), "Failed to create research note.")
                Result.failure(Exception(err))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteAnalysis(analysisId: String): Result<Boolean> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.deleteAnalysis(analysisId, token)
            if (response.isSuccessful) Result.success(true) else Result.failure(Exception("Failed to delete analysis."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun listDeletedAnalyses(): Result<List<AnalysisSummaryDto>> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.listDeletedAnalyses(token)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to list deleted analyses."))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun restoreAnalysis(analysisId: String): Result<Boolean> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.restoreAnalysis(analysisId, token)
            if (response.isSuccessful) Result.success(true) else Result.failure(Exception("Failed to restore analysis."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteNote(noteId: String): Result<Boolean> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.deleteNote(noteId, token)
            if (response.isSuccessful) Result.success(true) else Result.failure(Exception("Failed to delete note."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun listDeletedNotes(): Result<List<ResearchNoteDto>> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.listDeletedNotes(token)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to list deleted notes."))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun restoreNote(noteId: String): Result<Boolean> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.restoreNote(noteId, token)
            if (response.isSuccessful) Result.success(true) else Result.failure(Exception("Failed to restore note."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun listSavedComparisons(): Result<List<ComparisonDto>> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.listSavedComparisons(token)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val err = parseErrorMessage(response.errorBody()?.string(), "Failed to fetch comparisons.")
                Result.failure(Exception(err))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createSavedComparison(title: String, analysisIds: List<String>): Result<ComparisonDto> {
        val token = getBearerToken() ?: return Result.failure(Exception("Unauthenticated user."))
        return try {
            val response = apiService.createSavedComparison(token, ComparisonSaveRequest(title, analysisIds))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to save comparison."))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun parseErrorMessage(errorJson: String?, fallback: String): String {
        if (errorJson.isNullOrEmpty()) return fallback
        return try {
            val json = JSONObject(errorJson)
            json.optString("error_description", json.optString("detail", json.optString("message", fallback)))
        } catch (e: Exception) {
            fallback
        }
    }
}
