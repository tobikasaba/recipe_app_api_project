{*
  Server block for a single virtual host.
  Nginx reads server blocks to determine how to handle incoming requests.
*}
server {
    {*
      The TCP port on which Nginx will listen.
      Make sure this matches the port your application or proxy expects.
    *}
    listen ${LISTEN_PORT};

    {*
      Serve static assets directly from disk.
      All URIs beginning with /static/ are served from /vol/static
      (where Django’s collectstatic places them).
    *}
    location /static {
        alias /vol/static;
    }
    
    {*
      Proxy all other requests to the uWSGI application server:
      - uwsgi_pass: upstream address (e.g. ${APP_HOST}:${APP_PORT})
      - include: requeired to include uwisgi params. Standard uWSGI parameters are required of HTTP requests to be processed for header forwarding
      - client_max_body_size: permit uploads up to 10 MiB
    *}
    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10M;
    }
}