FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="tobikasaba"

# Copy your server config template into the container at location /etc/nginx/default.conf.tpl
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl

# Copy custom uWSGI parameter definitions for NGINX at location /etc/nginx/uwsgi_params
COPY ./uwsgi_params /etc/nginx/uwsgi_params

# Copy the entrypoint script that will set up and start NGINX into the image
COPY ./run.sh /run.sh

# Environment variables for port and uWSGI backend
ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

# Switch to root user to set up directories and permissions
USER root

# Create directory for static files
# Sets its permissions to 755. Owner rwx, group+others rx
# Ensures the NGINX site config file exists and is owned by the nginx user. Ensuring user can modify it
# Make entrypoint run.sh executable
RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

# Declare a volume so /vol/static can be mounted/filled at runtime
VOLUME /vol/static

# Drop privileges: run NGINX as the unprivileged nginx user
USER nginx

# Execute the run script, which will render the template and start NGINX
CMD ["/run.sh"]