FROM python:3.12-slim
WORKDIR /app
RUN useradd -r -u 10001 agentshield
COPY pyproject.toml .
COPY agentshield ./agentshield
RUN pip install --no-cache-dir .
USER agentshield
EXPOSE 8000
CMD ["uvicorn","agentshield.main:app","--host","0.0.0.0","--port","8000"]
