# Base image အနေနဲ့ Python 3.9 slim version ကိုသုံးမယ်
FROM python:3.12-slim

# Working directory သတ်မှတ်ခြင်း
WORKDIR /app

# Requirements ဖိုင်ကို copy လုပ်ခြင်း
COPY requirements.txt .

# Python packages တွေကို install လုပ်ခြင်း
RUN pip install --no-cache-dir -r requirements.txt

# Application code တွေကို copy လုပ်ခြင်း
COPY . .

# Environment variables တွေသတ်မှတ်ခြင်း
ENV FLASK_APP=src.server:flask_app
ENV FLASK_ENV=development
# Port ဖွင့်ပေးခြင်း (Gunicorn က 5555 port မှာ run မှာမို့)
EXPOSE 5000

# Gunicorn နဲ့ application ကို start လုပ်ခြင်း
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--reload", "src.server:flask_app"]