FROM python:3.9-alpine3.13
LABEL maintainer="tobikasaba"

# Prevents Python from buffering stdout/stderr (directly prints logs to the console)
ENV PYTHONUNBUFFERED 1

# Copy the requirements file into the Docker image at /tmp/requirements.txt
COPY ./requirements.txt /tmp/requirements.txt

# Copy the requirements.dev file into the Docker image at /tmp/requirements.dev.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy the application code into the Docker image at /app
COPY ./app /app

# Set the working directory to /app
WORKDIR /app

# Expose port 8000 for the container to listen on
EXPOSE 8000

#overridden to true when this file docker file is ran through requirements.dev and remains false elsewhere
ARG DEV=false


# A single RUN command is used because each RUN instruction creates a new image layer.
# Combining commands into a single RUN instruction and breaking it into multiple lines
# keeps the image lightweight and improves build performance.
RUN python -m venv /py && \
    # Upgrade pip inside the virtual environment.
    /py/bin/pip install --upgrade pip && \
    # Install Python dependencies listed in the requirements.txt file.
    /py/bin/pip install -r /tmp/requirements.txt && \
    # Install dev dependencies if the DEV is set to true
    if [$DEV = "true"]; \
      then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # Delete the /tmp directory to free up space.
    rm -rf /tmp && \
    # Add a new user named 'django-user' without a password or a home directory.
    # its best practice not to use the root user in the image, to run application.
    # in case of security compromise, hackers can only use features available to the created user
    adduser \
      --disabled-password \
      --no-create-home \
      django-user

#Updates the environment variable inside the image
#Activate the Virtual Environment by Default:
#To ensure the virtual environment is always active in the container, you can set the PATH environment variable:
ENV PATH="/py/bin:$PATH"

#specifies that we are switching to the django-user profile and not the default root user
USER django-user
