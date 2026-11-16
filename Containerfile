FROM docker.io/library/python:3.12-alpine
WORKDIR /app
COPY --chown=1001:0 app/ /app/
USER 1001
EXPOSE 8080
CMD ["python", "-m", "http.server", "8080", "--bind", "0.0.0.0", "--directory", "/app"]
