package com.simats.stainscope.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(entities = [ExperimentEntity::class, AnalysisResultEntity::class], version = 1, exportSchema = false)
abstract class StainScopeDatabase : RoomDatabase() {
    abstract fun analysisDao(): AnalysisDao

    companion object {
        @Volatile
        private var INSTANCE: StainScopeDatabase? = null

        fun getDatabase(context: Context): StainScopeDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    StainScopeDatabase::class.java,
                    "stainscope_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
