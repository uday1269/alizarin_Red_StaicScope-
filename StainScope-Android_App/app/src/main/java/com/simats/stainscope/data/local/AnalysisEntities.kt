package com.simats.stainscope.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "experiments")
data class ExperimentEntity(
    @PrimaryKey val id: String,
    val name: String,
    val cellLine: String,
    val incubationPeriod: String,
    val magnification: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "analysis_results")
data class AnalysisResultEntity(
    @PrimaryKey val analysisId: String,
    val experimentId: String,
    val mineralizedAreaPercent: Double,
    val noduleCount: Int,
    val opticalDensity: Double,
    val aiConfidence: Double,
    val imageUrl: String?,
    val analyzedAt: String?
)
