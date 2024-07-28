FROM python:3.12-slim

# Least privileged for security
# Info https://snyk.io/blog/best-practices-containerizing-python-docker/
RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python

# Mkdir as least privileged user
RUN mkdir /app && chown python:python /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy as least privileged user
COPY --chown=python:python . .

# Run the app as least privileged user
USER 999

# For development
#CMD ["python", "app.py"]

# For production
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "app:app" ]
HEALTHCHECK --interval=24h --timeout=30s --start-period=20s --retries=1 \
    CMD python /app/healthcheck.py