package ru.smarthome.sensorpoller

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.scheduling.annotation.EnableScheduling

@SpringBootApplication
@EnableScheduling
class SensorPollerApplication

fun main(args: Array<String>) {
    runApplication<SensorPollerApplication>(*args)
}

