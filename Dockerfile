FROM python:3.9-alpine3.13
LABEL authors="tobikasaba"

# Prevents Python from buffering stdout/stderr (directly prints logs to the console)
ENV PYTHONUNBUFFERED=1

# Copy the requirements file into the Docker image at /tmp/requirements.txt
COPY ./requirements.txt /tmp/requirements.txt

# Copy the application code into the Docker image at /app
COPY ./app /app

# Set the working directory to /app
WORKDIR /app

# Expose port 8000 for the container to listen on
EXPOSE 8000

#RUN python -m venv /py && \
#    /py/bin/pip install --upgrade pip && \
#    /py/bin/pip install -r /tmp/requirements.txt && \
#    rm -rf / tmp && \
#    adduser \
#      --disabled-password \
#      --no-create-home \ django-user

ENV PATH="/py/bin:$PATH"

ENTRYPOINT ["top", "-b"]