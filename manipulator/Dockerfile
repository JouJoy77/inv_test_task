FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .


CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8090"]
