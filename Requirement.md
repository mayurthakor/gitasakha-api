### Technical Requirement Document for GitaSakha Microservice

#### 1. **Introduction**
The GitaSakha mobile app will provide users with access to verses from the Bhagavad Gita, categorized by emotions and themes. The app will interact with a Python-based microservice that serves the verses from a JSON file (`gita-shloks.json`). This document outlines the technical requirements for developing the microservice, including API design, data handling, and deployment.

#### 2. **Objectives**
- Develop a RESTful API to serve Bhagavad Gita verses based on emotions and themes.
- Ensure the API is scalable, secure, and easy to integrate with the mobile app.
- Provide endpoints for retrieving verses, translations, and explanations.
- Deploy the microservice on a cloud server for accessibility.

#### 3. **Functional Requirements**
1. **API Endpoints**:
   - **GET /emotions**: Retrieve a list of all emotions and their associated themes.
   - **GET /emotions/{emotion}**: Retrieve details of a specific emotion, including its themes.
   - **GET /emotions/{emotion}/themes/{theme}**: Retrieve all shloks (verses) for a specific theme under an emotion.
   - **GET /shloks/{chapter}/{verse}**: Retrieve a specific shlok by chapter and verse number.
   - **GET /search?query={query}**: Search for shloks based on a keyword or phrase.

2. **Data Handling**:
   - The microservice will read data from the `gita-shloks.json` file.
   - The JSON structure will be parsed to extract relevant information for each endpoint.
   - The service should handle large JSON files efficiently.

3. **Error Handling**:
   - Return appropriate HTTP status codes (e.g., 404 for not found, 400 for bad requests).
   - Provide meaningful error messages in the response.

4. **Security**:
   - Implement API key authentication to restrict access to authorized clients.
   - Use HTTPS to encrypt data in transit.

5. **Performance**:
   - Optimize response times by caching frequently accessed data.
   - Implement rate limiting to prevent abuse.

#### 4. **Non-Functional Requirements**
1. **Scalability**:
   - The microservice should be able to handle a growing number of users and requests.
   - Use a load balancer and auto-scaling if deployed on a cloud platform.

2. **Availability**:
   - Ensure high availability with a minimum uptime of 99.9%.
   - Implement health checks and monitoring.

3. **Maintainability**:
   - Use a modular code structure for easy maintenance and updates.
   - Include logging for debugging and monitoring.

4. **Documentation**:
   - Provide comprehensive API documentation using Swagger or OpenAPI.
   - Include examples for each endpoint.

#### 5. **Technical Specifications**
1. **Programming Language**: Python 3.x
2. **Framework**: Flask or FastAPI (for building RESTful APIs)
3. **Data Storage**: JSON file (`gita-shloks.json`)
4. **Authentication**: API Key
5. **Deployment**:
   - **Cloud Platform**: AWS, Google Cloud, or Azure
   - **Containerization**: Docker
   - **Orchestration**: Kubernetes (optional for scaling)
6. **Caching**: Redis or in-memory caching
7. **Logging**: Python's logging module or a logging service like ELK stack.
8. **Monitoring**: Prometheus and Grafana for performance monitoring.

#### 6. **Development Setup**
1.  **Prerequisites**:
    -   Python 3.x
    -   pip (Python package installer)
    -   Virtualenv (optional but recommended)

2.  **Setup Instructions**:
    -   Clone the repository to your local machine.
    -   Create a virtual environment (optional):
        ```bash
        virtualenv venv
        source venv/bin/activate  # On Linux/macOS
        venv\Scripts\activate  # On Windows
        ```
    -   Install the required dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    -   Set the necessary environment variables (e.g., API keys, database connection strings).
    -   Run the application:
        ```bash
        python run.py
        ```

#### 7. **API Design**
1. **Base URL**: `https://api.gitasakha.com/v1`
2. **Endpoints**:
   - **GET /emotions**
     - **Response**:
       ```json
       {
         "emotions": [
           {
             "name": "joy",
             "emoji": "😊",
             "color": "#FFD700",
             "themes": ["true_happiness", "contentment"]
           },
           {
             "name": "trust",
             "emoji": "🙂",
             "color": "#90EE90",
             "themes": ["faith", "surrender"]
           }
         ]
       }
       ```
   - **GET /emotions/{emotion}**
     - **Response**:
       ```json
       {
         "name": "joy",
         "emoji": "😊",
         "color": "#FFD700",
         "themes": [
           {
             "name": "true_happiness",
             "description": "Verses about lasting happiness beyond material pleasures"
           },
           {
             "name": "contentment",
             "description": "Verses about finding joy in contentment"
           }
         ]
       }
       ```
   - **GET /emotions/{emotion}/themes/{theme}**
     - **Response**:
       ```json
       {
         "shloks": [
           {
             "chapter": 2,
             "verse": 38,
             "sanskrit": "सुखदुःखे समे कृत्वा लाभालाभौ जयाजयौ ।",
             "translation": {
               "english": "Having made pleasure and pain, gain and loss, victory and defeat the same, engage in battle for the sake of battle; thus you shall not incur sin.",
               "hindi": "सुख-दुःख, लाभ-हानि और जीत-हार को समान समझकर युद्ध के लिए युद्ध कर। ऐसा करने से तुझे पाप नहीं लगेगा।"
             },
             "explanation_url": "https://www.holy-bhagavad-gita.org/chapter/2/verse/38"
           }
         ]
       }
       ```
   - **GET /shloks/{chapter}/{verse}**
     - **Response**:
       ```json
       {
         "chapter": 2,
         "verse": 38,
         "sanskrit": "सुखदुःखे समे कृत्वा लाभालाभौ जयाजयौ ।",
         "translation": {
           "english": "Having made pleasure and pain, gain and loss, victory and defeat the same, engage in battle for the sake of battle; thus you shall not incur sin.",
           "hindi": "सुख-दुःख, लाभ-हानि और जीत-हार को समान समझकर युद्ध के लिए युद्ध कर। ऐसा करने से तुझे पाप नहीं लगेगा।"
         },
         "explanation_url": "https://www.holy-bhagavad-gita.org/chapter/2/verse/38"
       }
       ```
   - **GET /search?query={query}**
     - **Response**:
       ```json
       {
         "results": [
           {
             "chapter": 2,
             "verse": 38,
             "sanskrit": "सुखदुःखे समे कृत्वा लाभालाभौ जयाजयौ ।",
             "translation": {
               "english": "Having made pleasure and pain, gain and loss, victory and defeat the same, engage in battle for the sake of battle; thus you shall not incur sin.",
               "hindi": "सुख-दुःख, लाभ-हानि और जीत-हार को समान समझकर युद्ध के लिए युद्ध कर। ऐसा करने से तुझे पाप नहीं लगेगा।"
             },
             "explanation_url": "https://www.holy-bhagavad-gita.org/chapter/2/verse/38"
           }
         ]
       }
       ```

#### 7. **Deployment Strategy**
1. **Containerization**: Use Docker to containerize the microservice for easy deployment and scaling.
2. **Orchestration**: Use Kubernetes for managing containerized applications if scaling is required.
3. **Cloud Deployment**: Deploy on AWS (EC2, ECS, or EKS), Google Cloud (GKE), or Azure (AKS).
4. **CI/CD Pipeline**: Set up a CI/CD pipeline using GitHub Actions, Jenkins, or GitLab CI for automated testing and deployment.

#### 8. **Testing**
1. **Unit Testing**: Use `pytest` for unit testing individual components.
2. **Integration Testing**: Test the API endpoints using tools like Postman or `requests` library in Python.
3. **Load Testing**: Use tools like Apache JMeter or Locust to simulate high traffic and ensure the service can handle it.

#### 9. **Future Enhancements**
1. **User Authentication**: Allow users to create accounts and save favorite verses.
2. **Localization**: Support multiple languages for translations.
3. **Analytics**: Track usage patterns to improve the service.

#### 10. **Conclusion**
This document outlines the technical requirements for developing the GitaSakha microservice. By following these guidelines, you can build a robust, scalable, and secure API that serves Bhagavad Gita verses to the mobile app. Once the API is ready, it can be deployed on a cloud server for public access.
