# Stage 1: Build with Gradle
FROM gradle:8.7-jdk21 AS builder

WORKDIR /app

COPY gradle gradle
COPY build.gradle settings.gradle gradlew /app/
RUN ./gradlew --no-daemon build || true

COPY . .
RUN ./gradlew bootJar --no-daemon

# Stage 2: Run the built JAR
FROM eclipse-temurin:21-jdk-alpine

WORKDIR /app

COPY --from=builder /app/build/libs/*.jar app.jar

EXPOSE 8080

ENV SPRING_PROFILES_ACTIVE=docker

ENTRYPOINT ["java", "-jar", "app.jar"]
