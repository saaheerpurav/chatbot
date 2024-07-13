# Chatbot

This is a Flask web application that uses LlamaIndex. Returns a chat window to be used in an iframe. The application is optimized for deployment using Docker.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/saaheerpurav/chatbot.git
   cd chatbot
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Add environment variables**:
    Create an .env file with the following fields
    ```
    OPENAI_API_KEY=...
    FLASK_SECRET_KEY=...
    AWS_KEY=...
    AWS_SECRET=...
    DATABASE_URL=...
    ```

## Usage

1. **Run the flask application (dev)**:
    ```
    flask run --debug
    ```
    The application will be available at `http://127.0.0.1:5000`

2. **Run the flask application (production)**:
    ```
    waitress-serve --call app:create_app
    ```
    The application will be available at `http://0.0.0.0:8080`


## Deployment

1. **Build the Docker image**:

   ```bash
   docker build -t chatbot-container .
    ```

2. **Run the Docker container**:
    ```bash
    docker run -p 8080:8080 --env-file ./.env chatbot-container
    ```
    The application will be available at `http://localhost:8080`



