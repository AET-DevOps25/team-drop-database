# GenAI Route Recommendation for Travel

![Landing Page](documentation/images/landing-page.png)

This repository contains the source code and documentation for a GenAI-powered web application designed to deliver personalized travel itineraries using conversational AI to provide personalized attraction recommendation.

## Overview

Travel planning can be complex and tedious. This project addresses the issue by creating highly personalized itineraries, optimizing according to multiple user preferences, and offering real-time, reliable recommendations via AI.

![use-case-diagram](documentation/use_case_diagram.png)

### Intended Users

* **Independent Travelers** seeking personalized travel routes.
* **Industry Partners** (such as Ticket Booking Platforms) aiming to enhance their services with personalized route planning.

## Main Functionalities

### 1. Conversational Trip Builder

Interact naturally with an AI assistant to generate customized travel routes. Example:

* User input: "I have 5 days in Munich, architect fan and want to explore authentic local restaurants."
* Output: Personalized travel recommendation with explanation.

### 2. Preference-Aware Optimization

Routes are optimized based on user-defined preferences such as budget, scenic value, and accessibility. Preferences are persistently stored for continuous improvement over multiple sessions.

### 3. Reliable Recommendations

The system employs Retrieval-Augmented Generation (RAG) to recommend real-world attractions backed by current and verified information from reliable sources.

## System Architecture

* **Client Side:** Built with React.js, interacts with users via intuitive conversational UI.
* **Server Side:** Spring Boot for core business logic.
* **AI Components:** GenAI model (LLMs with RAG integration) for conversational reasoning and recommendations.
* **Persistence Layer:** PostgreSQL database for storing user preferences and session data.

![top_level_arch](documentation/top_level_arch.png)

## Installation and Setup

### Prerequisites

* Java 21 (for development setup)
* Node.js 18 or higher (for development setup)
* PostgreSQL (for development setup)
* Docker and Docker Compose (for Docker deployment - recommended)
* Python 3.11+ with Poetry (for GenAI service development)

### Steps

### Docker Setup (recommended)

1. **Clone Repository**

   ```sh
   git clone git@github.com:AET-DevOps25/team-drop-database.git
   cd team-drop-database
   ```
   
2. **Configure Environment Variables**

   Set up the necessary environment files for each service:
   ```sh
   # Copy example environment files and configure them
   cp genai/.env.example genai/.env
   # Edit genai/.env file with your OpenAI API key and other configurations
   
   # Other services use environment variables defined in docker-compose.yml
   ```

3. **One-Click Docker Deployment**

   For automatic deployment of all services:
   ```sh
   # Option 1: Use the provided script (recommended)
   ./start-docker-all.sh
   
   # Option 2: Use docker-compose directly
   docker-compose up --build
   ```

   This will automatically:
   - Build and start all microservices (AuthService, AttractionService, UserService)
   - Start the GenAI service
   - Start the React frontend
   - Set up PostgreSQL database with initial schema
   - Configure all service networking and dependencies

### Development Setup

1. **Clone Repository**

   ```sh
   git clone git@github.com:AET-DevOps25/team-drop-database.git
   ```

2. **Server Side Setup**

   ```sh
   cd server/AttractionService
   ./gradlew build
   ```

   ```sh
   cd server/AuthService
   ./gradlew build
   ```

   ```sh
   cd server/UserService
   ./gradlew build
   ```
   before running the microservices, make sure to set up the PostgreSQL database and update the `application.properties` files with your database credentials.
   you should also specify the profile to be "dev"

3. **GenAI Service Setup**

   ```sh
   cd genai
   ```

   Create and activate a virtual environment:
   ```sh
   # Using venv (recommended)
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   
   # Or using conda
   conda create -n travelbuddy python=3.11
   conda activate travelbuddy
   ```

   Install dependencies:
   ```sh
   # Install poetry if not already installed
   brew install poetry  # On macOS
   
   # Install project dependencies
   poetry install
   
   # Download required language model
   python -m spacy download en_core_web_sm
   ```

   Set up environment variables:
   ```sh
   cp .env.example .env
   # Edit .env file with your API keys and configuration
   ```

4. **Frontend Setup**

   ```sh
   cd client/travel-buddy
   npm install
   npm start
   ```

## Testing

The project includes comprehensive testing for all components:

### Running Tests

```sh
# Frontend tests only
cd client/travel-buddy
npm run test:ci

# Or use the convenience script
./test-frontend.sh

# Backend Java tests
cd server/AttractionService && ./gradlew test
cd server/AuthService && ./gradlew test  
cd server/UserService && ./gradlew test

# Python/GenAI tests
cd genai && pytest -v
```

### CI/CD Testing

All tests run automatically in GitHub Actions on every push and pull request. The pipeline includes:
- Frontend React/TypeScript tests with Jest
- Backend Java unit tests with Gradle
- Python tests with pytest

## Usage

* Access the application via `http://localhost:3000` or under `https://travel-buddy.student.k8s.aet.cit.tum.de/`
* Begin by providing preferences or directly interacting with the conversational AI.

## Student Responsibilities

| Student Name  | Responsibility                                                                                                                        |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------|
| Shuaiwei Yu   | 1. AuthService Implementation <br/> 2. Client Side Authentication & Conversation Page Implementation <br/> 3. Helm and K8S deployment |
| Haochuan Huai | 1. GenAI Service Implementation <br/> 2. AWS Deployment <br/> 3. Backend Attraction Service API Implementation <br/> 4. Frontend Attraction Detail Page Implementation |
| Zhiyuan Ni    | 1. Attraction Service Implementation <br/> 2. Grafana and Prometheus Implementation <br/> 3. Helm and K8S Deployment and Debugging <br/> 4. Frontend List View Implementation |

## Documentation

Additional detailed documentation, architectural diagrams, and API specifications can be found in the project’s [Confluence page](confluence-url).
