# Set base image (host OS)
FROM python:3.12-alpine

# By default, listen on port 8080
EXPOSE 8080/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY app.py .
COPY templates ./templates
COPY static/css ./static/css

# Specify the command to run on container start
CMD [ "python", "./app.py" ]

# docker build -t chatbot-container .
# docker run -p 8080:8080 --env-file ./.env chatbot-container
# docker system prune

# docker tag chatbot-container us-west3-docker.pkg.dev/durable-height-427320-e6/chatbot-container-repo/chatbot-container
# docker push us-west3-docker.pkg.dev/durable-height-427320-e6/chatbot-container-repo/chatbot-container