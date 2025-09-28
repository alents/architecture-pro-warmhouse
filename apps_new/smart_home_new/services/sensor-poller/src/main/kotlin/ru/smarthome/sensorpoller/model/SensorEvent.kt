package ru.smarthome.sensorpoller.model

data class SensorEvent(
    val sensorId: Long,
    val value: Double,
    val timestamp: String
)