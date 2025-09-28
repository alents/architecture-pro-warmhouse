package ru.smarthome.sensorpoller.repository

import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Repository

@Repository
class SensorRepository(private val jdbcTemplate: JdbcTemplate) {
    fun findAllSensorIds(): List<Long> {
        return jdbcTemplate.query("SELECT id FROM sensors") { rs, _ -> rs.getLong("id") }
    }
}