# Stage 1: Build with Gradle
FROM gradle:8.7-jdk21 AS builder

WORKDIR /app

COPY gradle gradle
COPY gradlew .
COPY build.gradle settings.gradle ./

RUN ./gradlew --no-daemon dependencies

COPY . .

RUN ./gradlew --no-daemon bootJar -x test

# Stage 2: Run the built JAR
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

COPY --from=builder /app/build/libs/*.jar app.jar

EXPOSE 8080
ENV SPRING_PROFILES_ACTIVE=docker
ENTRYPOINT ["java","-jar","app.jar"]
