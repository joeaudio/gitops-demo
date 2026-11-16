FROM docker.io/library/python:3.12-alpine@sha256:a61cbd76a882645de7f91423329fe43a67eed60d7da24f9e5331414bb3618b20
RUN apk upgrade --no-cache
WORKDIR /app
COPY --chown=1001:0 app/index.html app/style.css app/app.js app/advisories.json app/server.py /app/
USER 1001
EXPOSE 8080
CMD ["python", "/app/server.py"]
