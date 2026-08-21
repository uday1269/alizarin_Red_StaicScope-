package com.simats.stainscope.data.local

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface AnalysisDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExperiment(experiment: ExperimentEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAnalysisResult(result: AnalysisResultEntity)

    @Transaction
    @Query("SELECT * FROM experiments ORDER BY createdAt DESC")
    fun getAllExperimentsWithResults(): Flow<List<ExperimentWithResult>>

    @Query("SELECT * FROM experiments WHERE id = :id")
    suspend fun getExperimentById(id: String): ExperimentEntity?

    @Query("SELECT * FROM analysis_results WHERE experimentId = :experimentId")
    suspend fun getResultForExperiment(experimentId: String): AnalysisResultEntity?
}

data class ExperimentWithResult(
    @Embedded val experiment: ExperimentEntity,
    @Relation(
        parentColumn = "id",
        entityColumn = "experimentId"
    )
    val result: AnalysisResultEntity?
)
