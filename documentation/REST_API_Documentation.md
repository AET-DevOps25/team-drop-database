# Travel Buddy REST API Documentation

## Overview

This document describes the REST API endpoints for the Travel Buddy application, consisting of microservices for authentication, user management, attraction data, and AI-powered recommendations.

## Base URLs

| Service | Base URL (Development) | Base URL (Production) |
|---------|----------------------|---------------------|
| Auth Service | `http://localhost:8081/auth-service/api/v1` | `https://auth-service.travel-buddy.student.k8s.aet.cit.tum.de/auth-service/api/v1` |
| User Service | `http://localhost:8082/user-service/api/v1` | `https://user-service.travel-buddy.student.k8s.aet.cit.tum.de/user-service/api/v1` |
| Attraction Service | `http://localhost:8083/attraction-service/api/v1` | `https://attr-service.travel-buddy.student.k8s.aet.cit.tum.de/attraction-service/api/v1` |
| LLM Service | `http://localhost:8000/api/v1` | `https://llm-service.travel-buddy.student.k8s.aet.cit.tum.de/api/v1` |

## Authentication

JWT authentication required. Include token in Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Auth Service API

### Authentication Endpoints

#### Register User
```http
POST /auth/register
```
- **Body**: `RegisterRequest` (email, password, role)
- **Returns**: `AuthenticationResponse` or 400 if user exists

#### Login
```http
POST /auth/authenticate
```
- **Body**: `AuthenticationRequest` (email, password)
- **Returns**: `AuthenticationResponse`

#### Refresh Token
```http
POST /auth/refresh-token
```
- **Headers**: Authorization with refresh token
- **Returns**: New tokens via HttpServletResponse

### Connection Status
```http
GET /connection
```
- **Returns**: Connection status

---

## User Service API

### User Profile Management

#### Create User Profile
```http
POST /profiles
```
- **Auth**: Required (must match profile email)
- **Body**: `UserEntity`
- **Returns**: 201 with created profile or 400 for invalid data

#### Get User Profile by ID
```http
GET /profiles/{id}
```
- **Auth**: Required (must be self)
- **Returns**: `UserEntity` or 404

#### Get User Profile by Email
```http
GET /profiles/email/{email}
```
- **Auth**: Required (must match email)
- **Returns**: `UserEntity` or 404

#### Update User Profile
```http
PUT /profiles/{id}
```
- **Auth**: Required (must be self)
- **Body**: `UserEntity`
- **Returns**: Updated profile or 404

#### Delete User Profile
```http
DELETE /profiles/{id}
```
- **Auth**: Required (must be self)
- **Returns**: 204 or 404

### Conversation Management

#### Create New Conversation
```http
POST /conversations/{userId}
```
- **Auth**: Required (must be self)
- **Body**: `String` (prompt)
- **Returns**: 201 with `ConversationEntity` or 400

#### Create New Conversation by Email
```http
POST /conversations/email/{email}
```
- **Auth**: Required (must match email)
- **Body**: `PromptDTO`
- **Returns**: 201 with `ConversationEntity` or 400

#### Get Conversation Context
```http
GET /conversations/{conversationId}
```
- **Auth**: Required (must have access to conversation)
- **Returns**: `ConversationEntity` or 404

#### Resume Conversation
```http
PUT /conversations/{conversationId}
```
- **Auth**: Required (must have access to conversation)
- **Body**: `PromptDTO`
- **Returns**: Updated `ConversationEntity` or 400

#### Delete Conversation
```http
DELETE /conversations/{conversationId}
```
- **Auth**: Required (must have access to conversation)
- **Returns**: 204 or 404

#### Get Conversation History by User ID
```http
GET /conversations/h/{userId}
```
- **Auth**: Required (must be self)
- **Returns**: `List<ConversationDTO>` or 404/204

#### Get Conversation History by Email
```http
GET /conversations/h/email/{email}
```
- **Auth**: Required (must match email)
- **Returns**: `List<ConversationDTO>` or 404

### Connection Status
```http
GET /connection
```
- **Returns**: Connection status

---

## Attraction Service API

### Attraction Management

#### Get All Attractions (Paginated)
```http
GET /attractions?page=0&size=10&sortBy=name
```
- **Parameters**: page (default: 0), size (default: 10), sortBy (default: "name")
- **Returns**: `Page<AttractionEntity>`

#### Get Attractions by City (Paginated)
```http
GET /attractions/city/{city}?page=0&size=10&sortBy=name
```
- **Parameters**: page, size, sortBy
- **Returns**: `Page<AttractionEntity>`

#### Get Attraction by Name
```http
GET /attractions/{name}
```
- **Returns**: `AttractionEntity` or 404

#### Get Attraction by ID
```http
GET /attractions/id/{id}
```
- **Returns**: `AttractionEntity` or 404

#### Create Attraction
```http
POST /attractions
```
- **Body**: `AttractionEntity` (id must be null)
- **Returns**: 201 or 400 if id provided

#### Bulk Create Attractions
```http
POST /attractions/list
```
- **Body**: `List<AttractionDTO>`
- **Returns**: 201

#### Delete Attraction
```http
DELETE /attractions/{id}
```
- **Returns**: 204 or 404

### City Management

#### Get All Cities
```http
GET /cities
```
- **Returns**: `List<CityEntity>`

#### Get City by ID
```http
GET /cities/{id}
```
- **Returns**: `CityEntity` or 404

#### Create City
```http
POST /cities
```
- **Body**: `CityEntity`
- **Returns**: 201 with created city

#### Delete City
```http
DELETE /cities/{id}
```
- **Returns**: 204 or 404

### Connection Status
```http
GET /connection
```
- **Returns**: Connection status

---

## LLM Service API (GenAI)

### Travel Recommendations

#### Get Travel Recommendations
```http
POST /recommend
```
- **Body**: `RecommendRequest` (query, optional user_id)
- **Returns**: `RecommendResponse` (itinerary)
- **Error**: 400 if query empty

#### Ask Question about Attractions
```http
POST /ask
```
- **Body**: `QuestionRequest` (question)
- **Returns**: `QuestionResponse` (success, question, answer, results_count)
- **Error**: 400 if question empty, 503 if QA system unavailable

### Vector Search
```http
GET /vector/search?query=...&top_k=5
```
- **Parameters**: query, top_k (optional, default: 5)
- **Returns**: Search results

### Health Check
```http
GET /health
```
- **Returns**: Health status

### Metrics
```http
GET /metrics
```
- **Returns**: Prometheus metrics

---

## Monitoring Endpoints

All Spring Boot services expose:

```http
GET /actuator/prometheus  # Prometheus metrics
GET /actuator/health      # Health check
GET /actuator/info        # Service information
```

---

## Data Models

### RegisterRequest
- email: String
- password: String  
- role: Role enum

### AuthenticationRequest
- email: String
- password: String

### UserEntity
- id: Long
- email: String
- firstName: String
- lastName: String
- preferences: Object
- createdAt/updatedAt: Timestamp

### AttractionEntity
- id: Long
- name: String (unique, max 100 chars)
- description: String (TEXT)
- location: Location (latitude, longitude, address)
- city: CityEntity
- openingHours: List<OpeningHours>
- photos: List<URL>
- website: String

### ConversationEntity
- id: Long
- userId: Long
- messages: List<ChatMessageEntity>
- createdAt/updatedAt: Timestamp

### RecommendRequest
- query: String
- user_id: Optional<Integer>

### QuestionRequest
- question: String

---

## Notes

1. JWT tokens expire after 1 day (refresh tokens after 7 days)
2. All services use PostgreSQL database
3. Pagination uses zero-based indexing
4. All timestamps in ISO 8601 format (UTC)
5. LLM service requires OpenAI API key configuration
