FROM python:3.12

# Set PYTHONUNBUFFERED to avoid buffering output
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]