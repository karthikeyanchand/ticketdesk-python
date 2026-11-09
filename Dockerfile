FROM python:latest

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV TICKETDESK_ENV=production
EXPOSE 8000
CMD ["uvicorn", "ticketdesk.main:app", "--host", "0.0.0.0", "--port", "8000"]
