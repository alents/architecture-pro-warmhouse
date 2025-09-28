package ru.smarthome.sensorpoller.client

import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
import org.springframework.web.reactive.function.client.WebClient
import org.springframework.web.reactive.function.client.awaitBody
import ru.smarthome.sensorpoller.model.TemperatureResponse

@Component
class TemperatureClient(
    builder: WebClient.Builder,
    @Value("\${temperature.service.url}") private val baseUrl: String
) {
    private val client: WebClient = builder.baseUrl(baseUrl).build()

    suspend fun getTemperature(sensorId: Long): TemperatureResponse {
        return client.get()
            .uri("/temperature/{id}", sensorId)
            .retrieve()
            .awaitBody()
    }
}