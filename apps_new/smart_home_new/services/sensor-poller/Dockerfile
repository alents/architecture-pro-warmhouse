FROM gradle:9.0.0-jdk17 AS builder

# Рабочая директория внутри контейнера
WORKDIR /home/gradle/project

# Копируем скрипт сборки и кэшируем зависимости
COPY build.gradle.kts settings.gradle.kts ./
RUN gradle dependencies --no-daemon || return 0

# Копируем исходники собираем fat-jar
COPY src src

RUN gradle clean bootJar --no-daemon


FROM alpine/java:17-jre AS runtime

WORKDIR /app

# Копируем собранный jar из builder-стадии
COPY --from=builder /home/gradle/project/build/libs/*-SNAPSHOT.jar app.jar

# Запуск приложения
ENTRYPOINT ["java", "-jar", "app.jar"]

