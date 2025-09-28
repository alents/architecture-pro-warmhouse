package ru.smarthome.sensorpoller.service

import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import org.slf4j.LoggerFactory
import org.springframework.amqp.rabbit.core.RabbitTemplate
import org.springframework.beans.factory.annotation.Value
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service
import ru.smarthome.sensorpoller.client.TemperatureClient
import ru.smarthome.sensorpoller.model.SensorEvent
import ru.smarthome.sensorpoller.repository.SensorRepository
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset

@Service
class PollerService(
    private val sensorRepository: SensorRepository,
    private val temperatureClient: TemperatureClient,
    private val rabbitTemplate: RabbitTemplate,
    @Value("\${poller.exchange}") private val exchange: String,
    @Value("\${poller.routing-key}") private val routingKey: String
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Scheduled(fixedDelayString = "\${poller.interval.ms:5000}")
    fun poll() {
        val sensors = sensorRepository.findAllSensorIds()
        logger.info("Polling ${sensors.size} sensors...")

        kotlinx.coroutines.runBlocking {
            coroutineScope {
                val jobs = sensors.map { id ->
                    async {
                        try {
                            val response = temperatureClient.getTemperature(id)
                            val now = Instant.now()
                            val odt = now.atOffset(ZoneOffset.systemDefault().rules.getOffset(now));
                            val event = SensorEvent(
                                sensorId = id,
                                value = response.value,
                                timestamp = odt.toString()
                            )
                            rabbitTemplate.convertAndSend(exchange, routingKey, event)
                            logger.info("Published event: $event")
                        } catch (ex: Exception) {
                            logger.error("Failed to fetch temperature for sensor $id", ex)
                        }
                    }
                }
                jobs.forEach { it.await() }
            }
        }
    }
}