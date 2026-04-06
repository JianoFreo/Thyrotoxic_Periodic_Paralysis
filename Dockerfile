FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

COPY config/ config/
COPY model/ model/
COPY dao/ dao/
COPY service/ service/
COPY routes/ routes/
COPY ui/ ui/
COPY app.py streamlit_app.py ./

RUN mkdir -p /app/data
VOLUME ["/app/data"]

CMD ["python", "app.py", "--port", "5050"]