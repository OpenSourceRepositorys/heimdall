FROM python:3.8-alpine

COPY . /app
WORKDIR /app

RUN pip install pipenv fastapi uvicorn
RUN pipenv install
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]