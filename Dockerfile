FROM tiangolo/uvicorn-gunicorn-fastapi:latest

COPY . /app

WORKDIR /app

RUN pip install pipenv
RUN pipenv install

# Testing only
#RUN pipenv run python load_test_fixtures.py

EXPOSE 8000
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
