package ru.smarthome.sensorpoller.config

import org.springframework.amqp.core.TopicExchange
import org.springframework.amqp.rabbit.connection.ConnectionFactory
import org.springframework.amqp.rabbit.core.RabbitTemplate
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class RabbitConfig(@Value("\${poller.exchange}") private val exchangeName: String) {

    @Bean
    fun exchange(): TopicExchange = TopicExchange(exchangeName, true, false)

    @Bean
    fun messageConverter() = Jackson2JsonMessageConverter()

    @Bean
    fun rabbitTemplate(cf: ConnectionFactory): RabbitTemplate {
        val template = RabbitTemplate(cf)
        template.messageConverter = messageConverter()
        return template
    }
}