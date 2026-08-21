package com.simats.stainscope.data.network

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApiService {
    @POST("auth/login")
    suspend fun login(
        @Body request: AuthRequest
    ): Response<AuthResponse>

    @POST("auth/signup")
    suspend fun signup(
        @Body request: AuthRequest
    ): Response<AuthResponse>
}
