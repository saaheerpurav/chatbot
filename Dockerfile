# Set base image (host OS)
FROM python:3.12-alpine

# By default, listen on port 8080
EXPOSE 8080/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

# Copy the content of the local src directory to the working directory
COPY app ./app

# Specify the command to run on container start
CMD ["waitress-serve", "--call", "app:create_app"]



# Ensure ENV is set to prod
# docker system prune
# docker build -t chatbot-container .
# docker run -p 8080:8080 --env-file ./.env chatbot-container

# docker tag chatbot-container us-west3-docker.pkg.dev/durable-height-427320-e6/chatbot-container-repo/chatbot-container
# docker push us-west3-docker.pkg.dev/durable-height-427320-e6/chatbot-container-repo/chatbot-container